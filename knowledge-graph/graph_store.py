"""Persistent graph store — SQLite-backed entity and relationship storage.

Supports:
- CRUD for entities and relationships
- Neighbor traversal
- Shortest path
- Lineage (all ancestors)
- Full-text search on entity names/properties
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from schema import Entity, Relationship, domain_for_type


class GraphStore:
    SCHEMA = """
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        domain TEXT NOT NULL,
        properties TEXT NOT NULL DEFAULT '{}',
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS relationships (
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        rel_type TEXT NOT NULL,
        properties TEXT NOT NULL DEFAULT '{}',
        weight REAL NOT NULL DEFAULT 1.0,
        created_at REAL NOT NULL,
        PRIMARY KEY (source_id, target_id, rel_type)
    );

    CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
    CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
    CREATE INDEX IF NOT EXISTS idx_entities_domain ON entities(domain);
    CREATE INDEX IF NOT EXISTS idx_rels_source ON relationships(source_id);
    CREATE INDEX IF NOT EXISTS idx_rels_target ON relationships(target_id);
    CREATE INDEX IF NOT EXISTS idx_rels_type ON relationships(rel_type);

    CREATE VIRTUAL TABLE IF NOT EXISTS entity_fts USING fts5(
        id, name, entity_type, domain, properties,
        content='entities',
        content_rowid='rowid'
    );

    CREATE TRIGGER IF NOT EXISTS entities_ai AFTER INSERT ON entities BEGIN
        INSERT INTO entity_fts(rowid, id, name, entity_type, domain, properties)
        VALUES (new.rowid, new.id, new.name, new.entity_type, new.domain, new.properties);
    END;

    CREATE TRIGGER IF NOT EXISTS entities_ad AFTER DELETE ON entities BEGIN
        INSERT INTO entity_fts(entity_fts, rowid, id, name, entity_type, domain, properties)
        VALUES ('delete', old.rowid, old.id, old.name, old.entity_type, old.domain, old.properties);
    END;

    CREATE TRIGGER IF NOT EXISTS entities_au AFTER UPDATE ON entities BEGIN
        INSERT INTO entity_fts(entity_fts, rowid, id, name, entity_type, domain, properties)
        VALUES ('delete', old.rowid, old.id, old.name, old.entity_type, old.domain, old.properties);
        INSERT INTO entity_fts(rowid, id, name, entity_type, domain, properties)
        VALUES (new.rowid, new.id, new.name, new.entity_type, new.domain, new.properties);
    END;
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

    def _row_to_entity(self, row: sqlite3.Row) -> Entity:
        return Entity(
            id=row["id"],
            name=row["name"],
            entity_type=row["entity_type"],
            domain=row["domain"],
            properties=json.loads(row["properties"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_rel(self, row: sqlite3.Row) -> Relationship:
        return Relationship(
            source_id=row["source_id"],
            target_id=row["target_id"],
            rel_type=row["rel_type"],
            properties=json.loads(row["properties"]),
            weight=row["weight"],
            created_at=row["created_at"],
        )

    # --- Entity CRUD ---

    def create_entity(
        self,
        id: str,
        name: str,
        entity_type: str,
        properties: Optional[Dict] = None,
    ) -> Entity:
        domain = domain_for_type(entity_type)
        if not domain:
            raise ValueError(f"Unknown entity type: {entity_type}")
        now = time.time()
        props = json.dumps(properties or {})
        self._execute(
            """INSERT OR REPLACE INTO entities
               (id, name, entity_type, domain, properties, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (id, name, entity_type, domain, props, now, now),
        )
        return Entity(id, name, entity_type, domain, properties or {}, now, now)

    def get_entity(self, id: str) -> Optional[Entity]:
        row = self._execute(
            "SELECT * FROM entities WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_entity(row) if row else None

    def update_entity(self, id: str, properties: Optional[Dict] = None, name: Optional[str] = None) -> bool:
        updates = []
        params = []
        if properties is not None:
            updates.append("properties = ?")
            params.append(json.dumps(properties))
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if not updates:
            return False
        updates.append("updated_at = ?")
        params.append(time.time())
        params.append(id)
        self._execute(
            f"UPDATE entities SET {', '.join(updates)} WHERE id = ?",
            tuple(params),
        )
        return self._conn.total_changes > 0

    def delete_entity(self, id: str) -> bool:
        self._execute("DELETE FROM relationships WHERE source_id = ? OR target_id = ?", (id, id))
        self._execute("DELETE FROM entities WHERE id = ?", (id,))
        return self._conn.total_changes > 0

    def search_entities(self, query: str, domain: Optional[str] = None, limit: int = 20) -> List[Entity]:
        if domain:
            rows = self._execute(
                """SELECT * FROM entities
                   WHERE domain = ? AND (name LIKE ? OR id LIKE ?)
                   ORDER BY updated_at DESC LIMIT ?""",
                (domain, f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        else:
            rows = self._execute(
                """SELECT * FROM entities
                   WHERE name LIKE ? OR id LIKE ?
                   ORDER BY updated_at DESC LIMIT ?""",
                (f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        return [self._row_to_entity(r) for r in rows]

    def fts_search(self, query: str, limit: int = 20) -> List[Entity]:
        try:
            rows = self._execute(
                """SELECT e.* FROM entities e
                   JOIN entity_fts fts ON e.id = fts.id
                   WHERE entity_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (query, limit),
            ).fetchall()
            return [self._row_to_entity(r) for r in rows]
        except sqlite3.OperationalError:
            return self.search_entities(query, limit=limit)

    def list_entities_by_type(self, entity_type: str, limit: int = 100) -> List[Entity]:
        rows = self._execute(
            "SELECT * FROM entities WHERE entity_type = ? LIMIT ?",
            (entity_type, limit),
        ).fetchall()
        return [self._row_to_entity(r) for r in rows]

    def list_entities_by_domain(self, domain: str, limit: int = 100) -> List[Entity]:
        rows = self._execute(
            "SELECT * FROM entities WHERE domain = ? LIMIT ?",
            (domain, limit),
        ).fetchall()
        return [self._row_to_entity(r) for r in rows]

    # --- Relationship CRUD ---

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: Optional[Dict] = None,
        weight: float = 1.0,
    ) -> Relationship:
        now = time.time()
        props = json.dumps(properties or {})
        self._execute(
            """INSERT OR REPLACE INTO relationships
               (source_id, target_id, rel_type, properties, weight, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (source_id, target_id, rel_type, props, weight, now),
        )
        return Relationship(source_id, target_id, rel_type, properties or {}, weight, now)

    def delete_relationship(self, source_id: str, target_id: str, rel_type: str) -> bool:
        self._execute(
            "DELETE FROM relationships WHERE source_id = ? AND target_id = ? AND rel_type = ?",
            (source_id, target_id, rel_type),
        )
        return self._conn.total_changes > 0

    # --- Graph Queries ---

    def get_neighbors(
        self, entity_id: str, depth: int = 1, max_nodes: int = 100
    ) -> Dict[str, Any]:
        """BFS traversal returning subgraph centered on entity_id."""
        visited_entities: Set[str] = set()
        visited_rels: Set[Tuple[str, str, str]] = set()
        entities: Dict[str, Entity] = {}
        relationships: List[Dict] = []
        queue: List[Tuple[str, int]] = [(entity_id, 0)]

        while queue:
            current_id, current_depth = queue.pop(0)
            if current_depth > depth or current_id in visited_entities:
                continue
            if len(visited_entities) >= max_nodes:
                break

            visited_entities.add(current_id)
            entity = self.get_entity(current_id)
            if entity:
                entities[current_id] = entity

            if current_depth < depth:
                # Outgoing edges
                rows = self._execute(
                    "SELECT * FROM relationships WHERE source_id = ?", (current_id,)
                ).fetchall()
                for r in rows:
                    rel = self._row_to_rel(r)
                    key = (rel.source_id, rel.target_id, rel.rel_type)
                    if key not in visited_rels:
                        visited_rels.add(key)
                        relationships.append({
                            "source": rel.source_id,
                            "target": rel.target_id,
                            "type": rel.rel_type,
                            "weight": rel.weight,
                        })
                    queue.append((rel.target_id, current_depth + 1))

                # Incoming edges
                rows = self._execute(
                    "SELECT * FROM relationships WHERE target_id = ?", (current_id,)
                ).fetchall()
                for r in rows:
                    rel = self._row_to_rel(r)
                    key = (rel.source_id, rel.target_id, rel.rel_type)
                    if key not in visited_rels:
                        visited_rels.add(key)
                        relationships.append({
                            "source": rel.source_id,
                            "target": rel.target_id,
                            "type": rel.rel_type,
                            "weight": rel.weight,
                        })
                    queue.append((rel.source_id, current_depth + 1))

        return {
            "center": entity_id,
            "entities": {e.id: {
                "name": e.name,
                "type": e.entity_type,
                "domain": e.domain,
                "properties": e.properties,
            } for e in entities.values()},
            "relationships": relationships,
            "stats": {
                "entity_count": len(entities),
                "relationship_count": len(relationships),
                "depth": depth,
            },
        }

    def shortest_path(self, from_id: str, to_id: str) -> Optional[List[Dict]]:
        """BFS shortest path between two entities."""
        if from_id == to_id:
            return []

        visited: Set[str] = set()
        queue: List[Tuple[str, List[Dict]]] = [(from_id, [])]
        visited.add(from_id)

        while queue:
            current_id, path = queue.pop(0)
            rows = self._execute(
                "SELECT * FROM relationships WHERE source_id = ?", (current_id,)
            ).fetchall()
            for r in rows:
                rel = self._row_to_rel(r)
                if rel.target_id == to_id:
                    return path + [{
                        "source": rel.source_id,
                        "target": rel.target_id,
                        "type": rel.rel_type,
                        "weight": rel.weight,
                    }]
                if rel.target_id not in visited:
                    visited.add(rel.target_id)
                    queue.append(
                        (rel.target_id, path + [{
                            "source": rel.source_id,
                            "target": rel.target_id,
                            "type": rel.rel_type,
                            "weight": rel.weight,
                        }])
                    )

            # Also check incoming edges
            rows = self._execute(
                "SELECT * FROM relationships WHERE target_id = ?", (current_id,)
            ).fetchall()
            for r in rows:
                rel = self._row_to_rel(r)
                if rel.source_id == to_id:
                    return path + [{
                        "source": rel.source_id,
                        "target": rel.target_id,
                        "type": rel.rel_type,
                        "weight": rel.weight,
                    }]
                if rel.source_id not in visited:
                    visited.add(rel.source_id)
                    queue.append(
                        (rel.source_id, path + [{
                            "source": rel.source_id,
                            "target": rel.target_id,
                            "type": rel.rel_type,
                            "weight": rel.weight,
                        }])
                    )

        return None

    def lineage(self, entity_id: str) -> Dict[str, Any]:
        """All ancestors (transitive depends_on) and descendants."""
        entity = self.get_entity(entity_id)
        if not entity:
            return {"error": "Entity not found"}

        ancestors: List[Dict] = []
        descendants: List[Dict] = []

        def _walk_ancestors(current_id: str, depth: int = 0):
            if depth > 10:
                return
            rows = self._execute(
                "SELECT * FROM relationships WHERE target_id = ? AND rel_type = 'depends_on'",
                (current_id,),
            ).fetchall()
            for r in rows:
                rel = self._row_to_rel(r)
                e = self.get_entity(rel.source_id)
                if e:
                    ancestors.append({
                        "entity": e.name,
                        "type": e.entity_type,
                        "relationship": rel.rel_type,
                        "depth": depth + 1,
                    })
                    _walk_ancestors(rel.source_id, depth + 1)

        def _walk_descendants(current_id: str, depth: int = 0):
            if depth > 10:
                return
            rows = self._execute(
                "SELECT * FROM relationships WHERE source_id = ? AND rel_type = 'depends_on'",
                (current_id,),
            ).fetchall()
            for r in rows:
                rel = self._row_to_rel(r)
                e = self.get_entity(rel.target_id)
                if e:
                    descendants.append({
                        "entity": e.name,
                        "type": e.entity_type,
                        "relationship": rel.rel_type,
                        "depth": depth + 1,
                    })
                    _walk_descendants(rel.target_id, depth + 1)

        _walk_ancestors(entity_id)
        _walk_descendants(entity_id)

        return {
            "entity": entity.name,
            "entity_type": entity.entity_type,
            "ancestors": ancestors,
            "descendants": descendants,
            "ancestor_count": len(ancestors),
            "descendant_count": len(descendants),
        }

    def summary(self) -> str:
        ent_count = self._execute("SELECT COUNT(*) as c FROM entities").fetchone()["c"]
        rel_count = self._execute("SELECT COUNT(*) as c FROM relationships").fetchone()["c"]
        domain_counts = self._execute(
            "SELECT domain, COUNT(*) as c FROM entities GROUP BY domain ORDER BY c DESC"
        ).fetchall()
        domains = ", ".join(f"{r['domain']}={r['c']}" for r in domain_counts)
        return f"Entities: {ent_count} | Relationships: {rel_count} | Domains: [{domains}]"

    def close(self) -> None:
        self._conn.close()
