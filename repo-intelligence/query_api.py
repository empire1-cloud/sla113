"""Query API for the Repository Intelligence dependency graph.

Provides the same interface as the Empire Extension's repo_graph.py
but backed by persistent SQLite storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from graph_db import DepGraphDB


class RepoIntelligence:
    """High-level query interface over the persistent dep graph."""

    def __init__(self, db: DepGraphDB):
        self.db = db

    def depends_on(self, path: str) -> List[str]:
        """What does this file import?"""
        return [e["target"] for e in self.db.get_dependencies(path)]

    def what_breaks(self, path: str) -> List[str]:
        """What would break if this file changes (transitive dependents)."""
        return self.db.what_breaks(path)

    def code_paths_to(self, target: str) -> List[List[str]]:
        """All dependency chains from root files to target."""
        return self.db.code_paths_to(target)

    def engine_chain(self, repo_root: Path | None = None) -> List[str]:
        """Return pipeline order of registered engines."""
        engines = self.db.engines()
        if not engines:
            return []
        return [e["file"].rsplit("/", 1)[-1].replace(".py", "") for e in engines]

    def engines_json(self) -> List[Dict]:
        """Return engine registration data."""
        return self.db.engines()

    def find_files(self, query: str) -> List[str]:
        """Find files matching a name/path query."""
        rows = self.db._execute(
            "SELECT path FROM files WHERE path LIKE ? LIMIT 50",
            (f"%{query}%",),
        ).fetchall()
        return [r["path"] for r in rows]

    def summary(self) -> str:
        return self.db.summary()

    def find_dependents_by_symbol(self, symbol: str) -> List[str]:
        """Find all files that import a file which exports a given symbol."""
        exporters = self.db._execute(
            "SELECT file_path FROM exports WHERE symbol = ?", (symbol,)
        ).fetchall()
        results = set()
        for ex in exporters:
            deps = self.db.what_breaks(ex["file_path"])
            results.update(deps)
        return sorted(results)

    def close(self) -> None:
        self.db.close()
