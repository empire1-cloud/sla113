"""Persistent SQLite-backed dependency graph for repository intelligence.

Stores file-level dependency edges with change tracking.
Thread-safe, supports incremental updates.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class FileNode:
    path: str
    file_type: str  # py, ts, js, rs, go, etc.
    last_scanned: float
    imports: List[str] = field(default_factory=list)
    exported: List[str] = field(default_factory=list)
    hash: str = ""


@dataclass
class DepEdge:
    source: str
    target: str
    edge_type: str  # imports, extends, implements, calls
    line_no: int = 0


class DepGraphDB:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS files (
        path TEXT PRIMARY KEY,
        file_type TEXT NOT NULL,
        last_scanned REAL NOT NULL,
        hash TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS edges (
        source TEXT NOT NULL,
        target TEXT NOT NULL,
        edge_type TEXT NOT NULL DEFAULT 'imports',
        line_no INTEGER DEFAULT 0,
        first_seen REAL NOT NULL,
        last_seen REAL NOT NULL,
        PRIMARY KEY (source, target, edge_type)
    );

    CREATE TABLE IF NOT EXISTS exports (
        file_path TEXT NOT NULL,
        symbol TEXT NOT NULL,
        kind TEXT NOT NULL DEFAULT 'unknown',
        line_no INTEGER DEFAULT 0,
        PRIMARY KEY (file_path, symbol)
    );

    CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
    CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target);
    CREATE INDEX IF NOT EXISTS idx_exports_symbol ON exports(symbol);

    CREATE TABLE IF NOT EXISTS scan_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_root TEXT NOT NULL,
        files_scanned INTEGER NOT NULL,
        edges_found INTEGER NOT NULL,
        duration_ms REAL NOT NULL,
        scanned_at REAL NOT NULL
    );
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(self.SCHEMA)
        self._lock = __import__("threading").Lock()

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            return self._conn.execute(sql, params)

    def _executemany(self, sql: str, params: List[tuple]) -> sqlite3.Cursor:
        with self._lock:
            return self._conn.executemany(sql, params)

    def upsert_file(self, path: str, file_type: str, hash: str = "") -> None:
        now = time.time()
        self._execute(
            """INSERT INTO files (path, file_type, last_scanned, hash)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(path) DO UPDATE SET
                   last_scanned=excluded.last_scanned,
                   hash=excluded.hash""",
            (path, file_type, now, hash),
        )

    def remove_file(self, path: str) -> None:
        self._execute("DELETE FROM files WHERE path = ?", (path,))
        self._execute(
            "DELETE FROM edges WHERE source = ? OR target = ?", (path, path)
        )
        self._execute("DELETE FROM exports WHERE file_path = ?", (path,))

    def add_edge(
        self, source: str, target: str, edge_type: str = "imports", line_no: int = 0
    ) -> None:
        now = time.time()
        self._execute(
            """INSERT INTO edges (source, target, edge_type, line_no, first_seen, last_seen)
               VALUES (?, ?, ?, ?, ?, ?)
               ON CONFLICT(source, target, edge_type) DO UPDATE SET
                   last_seen=excluded.last_seen,
                   line_no=excluded.line_no""",
            (source, target, edge_type, line_no, now, now),
        )

    def add_export(self, file_path: str, symbol: str, kind: str = "", line_no: int = 0) -> None:
        self._execute(
            """INSERT INTO exports (file_path, symbol, kind, line_no)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(file_path, symbol) DO UPDATE SET
                   kind=excluded.kind, line_no=excluded.line_no""",
            (file_path, symbol, kind, line_no),
        )

    def log_scan(self, repo_root: str, files_scanned: int, edges_found: int, duration_ms: float) -> None:
        self._execute(
            "INSERT INTO scan_log (repo_root, files_scanned, edges_found, duration_ms, scanned_at) VALUES (?, ?, ?, ?, ?)",
            (repo_root, files_scanned, edges_found, duration_ms, time.time()),
        )

    def get_dependents(self, path: str) -> List[Dict]:
        """Everything that imports THIS file."""
        rows = self._execute(
            """SELECT source, edge_type, line_no FROM edges WHERE target = ?""",
            (path,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_dependencies(self, path: str) -> List[Dict]:
        """Everything THIS file imports."""
        rows = self._execute(
            """SELECT target, edge_type, line_no FROM edges WHERE source = ?""",
            (path,),
        ).fetchall()
        return [dict(r) for r in rows]

    def what_breaks(self, path: str) -> List[str]:
        """Recursive dependents — everything that would break if path changes."""
        visited: Set[str] = set()
        to_visit: List[str] = [path]
        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)
            deps = self._execute(
                "SELECT source FROM edges WHERE target = ?", (current,)
            ).fetchall()
            for d in deps:
                if d["source"] not in visited:
                    to_visit.append(d["source"])
        return sorted(visited - {path})

    def code_paths_to(self, target_path: str) -> List[List[str]]:
        """Find all dependency chains from root files to target_path."""
        roots = self._execute(
            """SELECT DISTINCT source FROM edges
               WHERE source NOT IN (SELECT target FROM edges)"""
        ).fetchall()
        target = target_path

        all_paths: List[List[str]] = []

        def _dfs(current: str, visited: Set[str], path: List[str]):
            if current == target:
                all_paths.append(path + [current])
                return
            if current in visited:
                return
            visited.add(current)
            edges = self._execute(
                "SELECT target FROM edges WHERE source = ?", (current,)
            ).fetchall()
            for e in edges:
                _dfs(e["target"], visited, path + [current])
            visited.discard(current)

        for root in roots:
            _dfs(root["source"], set(), [])

        return all_paths

    def engines(self) -> List[Dict]:
        """Find files that register as engines (decorators, registry calls)."""
        rows = self._execute(
            """SELECT DISTINCT e.source as file, e.target as registered_in,
                      e.edge_type, e.line_no
               FROM edges e
               WHERE e.edge_type IN ('decorator_register', 'registry_call')
               ORDER BY e.source"""
        ).fetchall()
        return [dict(r) for r in rows]

    def summary(self) -> str:
        file_count = self._execute("SELECT COUNT(*) as c FROM files").fetchone()["c"]
        edge_count = self._execute("SELECT COUNT(*) as c FROM edges").fetchone()["c"]
        export_count = self._execute("SELECT COUNT(*) as c FROM exports").fetchone()["c"]
        scan_count = self._execute("SELECT COUNT(*) as c FROM scan_log").fetchone()["c"]
        last_scan = self._execute(
            "SELECT scanned_at FROM scan_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        last = ""
        if last_scan:
            import datetime
            last = datetime.datetime.fromtimestamp(last_scan["scanned_at"]).isoformat()
        return (
            f"Files: {file_count} | Edges: {edge_count} | "
            f"Exports: {export_count} | Scans: {scan_count}"
            + (f" | Last: {last}" if last else "")
        )

    def close(self) -> None:
        self._conn.close()
