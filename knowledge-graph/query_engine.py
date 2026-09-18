"""Query engine — natural language to graph queries, plus programmatic API.

Parses simple NL patterns like:
  "what breaks if I change HarmonyEngine"  → lineage + dependency traversal
  "who owns arrangement_engine.py"         → entity lookup by name + owns_entity relationship
  "which competitors build stem separation" → domain filter on BUSINESS
  "find all code paths to master.wav"      → depends_on chain

Also provides the full programmatic query API.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set

from graph_store import GraphStore
from schema import list_domains, list_entity_types


class QueryEngine:
    def __init__(self, store: GraphStore):
        self.store = store

    def query(self, query_text: str, limit: int = 20) -> Dict[str, Any]:
        """Natural language to graph query."""
        q = query_text.strip().lower()

        # Pattern: "what breaks if I change <name>"
        m = re.search(r"(?:what|who)\s+breaks\s+(?:if|when)\s+(?:\w+\s+)*(?:change|modify|edit|delete|remove|touch)\s+(\S+)", q)
        if m:
            target = m.group(1)
            entities = self.store.search_entities(target, limit=5)
            if not entities:
                return {"error": f"Entity '{target}' not found", "query": query_text}
            all_breakers: Set[str] = set()
            for e in entities:
                neighbors = self.store.get_neighbors(e.id, depth=3)
                for eid, edata in neighbors.get("entities", {}).items():
                    if eid != e.id:
                        all_breakers.add(f"{edata['name']} ({edata['type']})")
            return {
                "query": query_text,
                "target": target,
                "breaks": sorted(all_breakers)[:limit],
                "count": len(all_breakers),
            }

        # Pattern: "who owns <name>" or "who created <name>"
        m = re.search(r"(?:who|what)\s+(owns?|created?|authored?|reviewed?|assigned?)\s+(?:the\s+)?(\S+)", q)
        if m:
            rel_type = {"own": "owns_entity", "create": "created_by", "author": "created_by",
                        "review": "reviewed_by", "assign": "assigned_to"}.get(m.group(1), "owns_entity")
            target = m.group(2)
            entities = self.store.search_entities(target, limit=5)
            if not entities:
                return {"error": f"Entity '{target}' not found", "query": query_text}
            results = []
            for e in entities:
                rels = self.store.shortest_path(e.id, "__any__")
                # For now, look through neighbors
                neighbors = self.store.get_neighbors(e.id, depth=1)
                for rid, rdata in neighbors.get("entities", {}).items():
                    results.append({"entity": e.name, "related": rdata["name"], "type": rdata["type"]})
            return {
                "query": query_text,
                "relationship": rel_type,
                "results": results[:limit],
                "count": len(results),
            }

        # Pattern: "find all code paths to <name>"
        m = re.search(r"(?:find|show|get|list)\s+(?:all\s+)?(?:code\s+)?paths?\s+(?:to|for|from)\s+(\S+)", q)
        if m:
            target = m.group(1)
            entities = self.store.search_entities(target, limit=5)
            if not entities:
                return {"error": f"Entity '{target}' not found", "query": query_text}
            paths = []
            for e in entities:
                lineage = self.store.lineage(e.id)
                paths.append(lineage)
            return {
                "query": query_text,
                "target": target,
                "paths": paths,
                "count": len(paths),
            }

        # Pattern: "list <domain>" or "show <type>"
        for domain_name in list_domains():
            if domain_name.lower() in q:
                entities = self.store.list_entities_by_domain(domain_name, limit=limit)
                return {
                    "query": query_text,
                    "domain": domain_name,
                    "entities": [{"id": e.id, "name": e.name, "type": e.entity_type} for e in entities],
                    "count": len(entities),
                }

        for entity_type in list_entity_types():
            if entity_type.lower() in q:
                entities = self.store.list_entities_by_type(entity_type, limit=limit)
                return {
                    "query": query_text,
                    "entity_type": entity_type,
                    "entities": [{"id": e.id, "name": e.name, "type": e.entity_type} for e in entities],
                    "count": len(entities),
                }

        # Fallback: full-text search
        entities = self.store.fts_search(query_text, limit=limit)
        if entities:
            return {
                "query": query_text,
                "results": [{"id": e.id, "name": e.name, "type": e.entity_type, "domain": e.domain} for e in entities],
                "count": len(entities),
                "method": "fts",
            }

        return {"error": "No matches found", "query": query_text}

    def get(self, entity_id: str) -> Optional[Dict]:
        entity = self.store.get_entity(entity_id)
        if not entity:
            return None
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.entity_type,
            "domain": entity.domain,
            "properties": entity.properties,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def neighbors(self, entity_id: str, depth: int = 2) -> Dict:
        return self.store.get_neighbors(entity_id, depth=depth)

    def shortest_path(self, from_id: str, to_id: str) -> Optional[List]:
        return self.store.shortest_path(from_id, to_id)

    def lineage(self, entity_id: str) -> Dict:
        return self.store.lineage(entity_id)

    def summary(self) -> str:
        return self.store.summary()
