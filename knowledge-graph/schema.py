"""Knowledge Graph schema — domain, entity type, and relationship definitions.

Seven domains: CODE, PROJECTS, PEOPLE, TASKS, AI, BUSINESS, INFRASTRUCTURE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


DOMAINS = {
    "CODE": "Source code entities — classes, functions, modules, engines, services",
    "PROJECTS": "Project artifacts — repos, roadmaps, PRDs, ADRs, docs",
    "PEOPLE": "Human entities — contributors, reviewers, owners, stakeholders",
    "TASKS": "Work items — TODOs, issues, PRs, emails, decisions, action items",
    "AI": "AI entities — skills, agents, memories, evaluations, runs",
    "BUSINESS": "Business entities — customers, products, revenue, competitors, trends",
    "INFRASTRUCTURE": "Infrastructure — servers, containers, deployments, pipelines, secrets",
}


ENTITY_TYPES = {
    # CODE
    "Module": "CODE",
    "Class": "CODE",
    "Function": "CODE",
    "Engine": "CODE",
    "Service": "CODE",
    "Router": "CODE",
    "Route": "CODE",
    "Model": "CODE",
    "API": "CODE",
    # PROJECTS
    "Repository": "PROJECTS",
    "Roadmap": "PROJECTS",
    "PRD": "PROJECTS",
    "ADR": "PROJECTS",
    "ArchitectureDoc": "PROJECTS",
    # PEOPLE
    "Person": "PEOPLE",
    "Team": "PEOPLE",
    "Role": "PEOPLE",
    # TASKS
    "Task": "TASKS",
    "Issue": "TASKS",
    "PullRequest": "TASKS",
    "Email": "TASKS",
    "Decision": "TASKS",
    "ActionItem": "TASKS",
    # AI
    "Skill": "AI",
    "Agent": "AI",
    "Memory": "AI",
    "Evaluation": "AI",
    "Run": "AI",
    # BUSINESS
    "Customer": "BUSINESS",
    "Product": "BUSINESS",
    "Competitor": "BUSINESS",
    "Trend": "BUSINESS",
    "Revenue": "BUSINESS",
    # INFRASTRUCTURE
    "Server": "INFRASTRUCTURE",
    "Container": "INFRASTRUCTURE",
    "Deployment": "INFRASTRUCTURE",
    "Pipeline": "INFRASTRUCTURE",
    "Secret": "INFRASTRUCTURE",
    "CloudResource": "INFRASTRUCTURE",
}


RELATIONSHIP_TYPES = {
    # CODE relationships
    "owns": {"source": "Module", "target": "Module", "description": "Module owns sub-module or file"},
    "depends_on": {"source": None, "target": None, "description": "Entity depends on another"},
    "implements": {"source": None, "target": None, "description": "Entity implements interface/class"},
    "extends": {"source": "Class", "target": "Class", "description": "Class extends another"},
    "breaks_if_changed": {"source": None, "target": None, "description": "Source breaks if target changes"},
    # PROJECTS relationships
    "documents": {"source": None, "target": None, "description": "Source documents target"},
    "supersedes": {"source": "ADR", "target": "ADR", "description": "ADR supersedes another"},
    "references": {"source": None, "target": None, "description": "Entity references another"},
    "introduced_by": {"source": None, "target": None, "description": "Entity introduced by PR/commit"},
    # PEOPLE relationships
    "created_by": {"source": None, "target": "Person", "description": "Entity created by person"},
    "reviewed_by": {"source": None, "target": "Person", "description": "Entity reviewed by person"},
    "assigned_to": {"source": None, "target": "Person", "description": "Entity assigned to person"},
    "owns_entity": {"source": "Person", "target": None, "description": "Person owns entity"},
    # TASKS relationships
    "blocks": {"source": "Task", "target": "Task", "description": "Task blocks another"},
    "related_to": {"source": None, "target": None, "description": "Related entities"},
    "generated_from": {"source": None, "target": None, "description": "Generated from source"},
    "resolves": {"source": "PullRequest", "target": "Issue", "description": "PR resolves issue"},
    # AI relationships
    "used_by": {"source": "Skill", "target": None, "description": "Skill used by entity"},
    "trained_on": {"source": "Agent", "target": None, "description": "Agent trained on data"},
    "produced_by": {"source": None, "target": "Agent", "description": "Produced by agent"},
    "evaluated_by": {"source": None, "target": "Evaluation", "description": "Evaluated by evaluation run"},
    # BUSINESS relationships
    "competes_with": {"source": "Competitor", "target": "Competitor", "description": "Competes with"},
    "serves": {"source": "Product", "target": "Customer", "description": "Product serves customer"},
    "monetizes": {"source": "Product", "target": "Revenue", "description": "Product generates revenue"},
    # INFRASTRUCTURE relationships
    "hosts": {"source": "Server", "target": None, "description": "Server hosts service"},
    "deploys_to": {"source": "Deployment", "target": "Server", "description": "Deployment targets server"},
    "connects_to": {"source": None, "target": None, "description": "Network connection"},
}


@dataclass
class Entity:
    id: str
    name: str
    entity_type: str
    domain: str
    properties: Dict = field(default_factory=dict)
    created_at: float = 0.0
    updated_at: float = 0.0


@dataclass
class Relationship:
    source_id: str
    target_id: str
    rel_type: str
    properties: Dict = field(default_factory=dict)
    weight: float = 1.0
    created_at: float = 0.0


def domain_for_type(entity_type: str) -> Optional[str]:
    return ENTITY_TYPES.get(entity_type)


def is_valid_entity_type(entity_type: str) -> bool:
    return entity_type in ENTITY_TYPES


def is_valid_rel_type(rel_type: str) -> bool:
    return rel_type in RELATIONSHIP_TYPES


def list_domains() -> Dict[str, str]:
    return dict(DOMAINS)


def list_entity_types(domain: Optional[str] = None) -> Dict[str, str]:
    if domain:
        return {k: v for k, v in ENTITY_TYPES.items() if v == domain}
    return dict(ENTITY_TYPES)


def list_relationship_types() -> Dict[str, Dict]:
    return dict(RELATIONSHIP_TYPES)
