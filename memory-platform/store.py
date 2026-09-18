"""Memory Platform — tiered persistent memory with recall.

Seven tiers:
  - WORKING: Current session context (auto-expires)
  - EPISODIC: Past sessions, decisions, dead ends
  - SEMANTIC: Facts, concepts, domain knowledge
  - PROCEDURAL: Workflows, recipes, how-to patterns
  - PROJECT: Per-project context and history
  - REPOSITORY: Per-repo conventions and changelogs
  - DECISION: Past decisions with tradeoffs and confidence
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


TIERS = {
    "WORKING": "Current task context, active files, recent messages. Auto-expires.",
    "EPISODIC": "Past sessions, decisions made, dead ends hit. Persistent.",
    "SEMANTIC": "Facts, concepts, domain knowledge. Persistent.",
    "PROCEDURAL": "Workflows, recipes, how-to patterns. Persistent.",
    "PROJECT": "Per-project context, conventions, history. Project lifetime.",
    "REPOSITORY": "Per-repo conventions, ADRs, deploy flow. Repo lifetime.",
    "DECISION": "Past decisions, tradeoffs, confidence scores. Permanent.",
}

TIER_RETENTION = {
    "WORKING": 86400 * 7,       # 7 days
    "EPISODIC": 86400 * 90,     # 90 days
    "SEMANTIC": 86400 * 365,    # 1 year
    "PROCEDURAL": 86400 * 365,  # 1 year
    "PROJECT": None,            # project lifetime
    "REPOSITORY": None,         # repo lifetime
    "DECISION": None,           # permanent
}

TIER_EXPIRY_CHECK_SECONDS = 3600  # Check for expired entries every hour


@dataclass
class MemoryEntry:
    id: str
    tier: str
    content: str
    tags: List[str] = field(default_factory=list)
    source: str = ""
    relevance: float = 1.0
    created_at: float = 0.0
    accessed_at: float = 0.0
    metadata: Dict = field(default_factory=dict)


class MemoryStore:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        tier TEXT NOT NULL,
        content TEXT NOT NULL,
        tags TEXT NOT NULL DEFAULT '[]',
        source TEXT NOT NULL DEFAULT '',
        relevance REAL NOT NULL DEFAULT 1.0,
        created_at REAL NOT NULL,
        accessed_at REAL NOT NULL,
        expires_at REAL,
        metadata TEXT NOT NULL DEFAULT '{}'
    );

    CREATE INDEX IF NOT EXISTS idx_memories_tier ON memories(tier);
    CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
    CREATE INDEX IF NOT EXISTS idx_memories_expires ON memories(expires_at);

    CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
        content, tags, source,
        content='memories',
        content_rowid='rowid'
    );

    CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
        INSERT INTO memories_fts(rowid, content, tags, source)
        VALUES (new.rowid, new.content, new.tags, new.source);
    END;

    CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, content, tags, source)
        VALUES ('delete', old.rowid, old.content, old.tags, old.source);
    END;

    CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, content, tags, source)
        VALUES ('delete', old.rowid, old.content, old.tags, old.source);
        INSERT INTO memories_fts(rowid, content, tags, source)
        VALUES (new.rowid, new.content, new.tags, new.source);
    END;

    CREATE TABLE IF NOT EXISTS memory_vectors (
        memory_id TEXT PRIMARY KEY,
        vector BLOB,
        model TEXT NOT NULL DEFAULT 'tfidf',
        updated_at REAL NOT NULL
    );
    """

    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(self.SCHEMA)
        self._lock = __import__("threading").Lock()
        self._last_expiry_check = 0.0

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            return self._conn.execute(sql, params)

    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            id=row["id"],
            tier=row["tier"],
            content=row["content"],
            tags=json.loads(row["tags"]),
            source=row["source"],
            relevance=row["relevance"],
            created_at=row["created_at"],
            accessed_at=row["accessed_at"],
            metadata=json.loads(row["metadata"]),
        )

    def _expire_old(self):
        """Remove expired entries."""
        now = time.time()
        if now - self._last_expiry_check < TIER_EXPIRY_CHECK_SECONDS:
            return
        self._last_expiry_check = now
        self._execute(
            "DELETE FROM memories WHERE expires_at IS NOT NULL AND expires_at < ?",
            (now,),
        )

    def is_valid_tier(self, tier: str) -> bool:
        return tier.upper() in TIERS

    def store(
        self,
        content: str,
        tier: str = "WORKING",
        tags: Optional[List[str]] = None,
        source: str = "",
        relevance: float = 1.0,
        metadata: Optional[Dict] = None,
    ) -> MemoryEntry:
        tier = tier.upper()
        if tier not in TIERS:
            raise ValueError(f"Invalid tier: {tier}. Valid: {', '.join(TIERS.keys())}")

        self._expire_old()

        import uuid
        entry_id = str(uuid.uuid4())
        now = time.time()
        retention = TIER_RETENTION.get(tier)
        expires_at = (now + retention) if retention else None

        self._execute(
            """INSERT INTO memories
               (id, tier, content, tags, source, relevance, created_at, accessed_at, expires_at, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry_id,
                tier,
                content,
                json.dumps(tags or []),
                source,
                relevance,
                now,
                now,
                expires_at,
                json.dumps(metadata or {}),
            ),
        )

        return MemoryEntry(
            id=entry_id,
            tier=tier,
            content=content,
            tags=tags or [],
            source=source,
            relevance=relevance,
            created_at=now,
            accessed_at=now,
            metadata=metadata or {},
        )

    def recall(self, query: str, tier: Optional[str] = None, limit: int = 20) -> List[MemoryEntry]:
        """Full-text search across memories, optionally filtered by tier."""
        self._expire_old()

        if tier:
            tier = tier.upper()
            if tier not in TIERS:
                return []

        try:
            if tier:
                rows = self._execute(
                    """SELECT m.* FROM memories m
                       JOIN memories_fts fts ON m.id = fts.id
                       WHERE memories_fts MATCH ? AND m.tier = ?
                       ORDER BY rank LIMIT ?""",
                    (query, tier, limit),
                ).fetchall()
            else:
                rows = self._execute(
                    """SELECT m.* FROM memories m
                       JOIN memories_fts fts ON m.id = fts.id
                       WHERE memories_fts MATCH ?
                       ORDER BY rank LIMIT ?""",
                    (query, limit),
                ).fetchall()
        except sqlite3.OperationalError:
            # FTS query parse error — fall back to LIKE
            if tier:
                rows = self._execute(
                    """SELECT * FROM memories
                       WHERE content LIKE ? AND tier = ?
                       ORDER BY relevance DESC, created_at DESC LIMIT ?""",
                    (f"%{query}%", tier, limit),
                ).fetchall()
            else:
                rows = self._execute(
                    """SELECT * FROM memories
                       WHERE content LIKE ?
                       ORDER BY relevance DESC, created_at DESC LIMIT ?""",
                    (f"%{query}%", limit),
                ).fetchall()

        results = [self._row_to_entry(r) for r in rows]

        # Update accessed_at for recalled entries
        for entry in results:
            self._execute(
                "UPDATE memories SET accessed_at = ? WHERE id = ?",
                (time.time(), entry.id),
            )

        return results

    def get(self, entry_id: str) -> Optional[MemoryEntry]:
        row = self._execute(
            "SELECT * FROM memories WHERE id = ?", (entry_id,)
        ).fetchone()
        if row:
            self._execute(
                "UPDATE memories SET accessed_at = ? WHERE id = ?",
                (time.time(), entry_id),
            )
            return self._row_to_entry(row)
        return None

    def forget(self, entry_id: str) -> bool:
        self._execute("DELETE FROM memories WHERE id = ?", (entry_id,))
        return self._conn.total_changes > 0

    def forget_tier(self, tier: str) -> int:
        tier = tier.upper()
        if tier not in TIERS:
            return 0
        self._execute("DELETE FROM memories WHERE tier = ?", (tier,))
        return self._conn.total_changes

    def summarize(self, tier: Optional[str] = None, since: Optional[float] = None) -> str:
        """Generate a text summary of memories."""
        where_clauses = []
        params = []

        if tier:
            tier = tier.upper()
            if tier not in TIERS:
                return f"Invalid tier: {tier}"
            where_clauses.append("tier = ?")
            params.append(tier)
        if since is not None:
            where_clauses.append("created_at >= ?")
            params.append(since)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        rows = self._execute(
            f"""SELECT tier, COUNT(*) as count,
                       MAX(created_at) as latest,
                       MIN(created_at) as earliest,
                       AVG(relevance) as avg_relevance
                FROM memories {where_sql}
                GROUP BY tier
                ORDER BY tier""",
            tuple(params),
        ).fetchall()

        if not rows:
            if tier:
                return f"No memories in tier '{tier}'."
            return "No memories found."

        lines = ["## Memory Summary", ""]
        for r in rows:
            lines.append(f"### {r['tier']}")
            lines.append(f"- Entries: {r['count']}")
            lines.append(f"- Date range: {time.ctime(r['earliest'])} → {time.ctime(r['latest'])}")
            lines.append(f"- Avg relevance: {r['avg_relevance']:.2f}")
            lines.append("")

            # Recent entries
            recent = self._execute(
                """SELECT content, tags, source, created_at FROM memories
                   WHERE tier = ?
                   ORDER BY created_at DESC LIMIT 5""",
                (r["tier"],),
            ).fetchall()
            if recent:
                lines.append("  Recent entries:")
                for e in recent:
                    content_preview = e["content"][:100].replace("\n", " ")
                    lines.append(f"  - {time.ctime(e['created_at'])}: {content_preview}...")
                lines.append("")

        return "\n".join(lines)

    def search(
        self,
        query: str,
        tier: Optional[str] = None,
        k: int = 10,
    ) -> List[MemoryEntry]:
        """Vector-like search using FTS5 with keyword overlap scoring."""
        return self.recall(query, tier=tier, limit=k)

    def export_tier(self, tier: str) -> List[Dict]:
        tier = tier.upper()
        if tier not in TIERS:
            return []
        rows = self._execute(
            "SELECT * FROM memories WHERE tier = ? ORDER BY created_at DESC",
            (tier,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "content": r["content"],
                "tags": json.loads(r["tags"]),
                "source": r["source"],
                "relevance": r["relevance"],
                "created_at": r["created_at"],
                "metadata": json.loads(r["metadata"]),
            }
            for r in rows
        ]

    def summary(self) -> str:
        counts = self._execute(
            "SELECT tier, COUNT(*) as c FROM memories GROUP BY tier ORDER BY c DESC"
        ).fetchall()
        if not counts:
            return "Memory Platform: empty"
        tiers = ", ".join(f"{r['tier']}={r['c']}" for r in counts)
        total = sum(r["c"] for r in counts)
        return f"Memory Platform: {total} entries [{tiers}]"

    def close(self) -> None:
        self._conn.close()
