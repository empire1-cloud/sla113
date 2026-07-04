"""AST-based import scanner for Python repositories.

Discovers files, parses import/export relationships, registration patterns.
Supports incremental scanning (only re-parse changed files).
"""

from __future__ import annotations

import ast
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from graph_db import DepGraphDB


REGISTRY_PATTERNS = {
    "register_engine": "decorator_register",
    "router.register": "registry_call",
    "orchestrator.register": "registry_call",
    "registry.register": "registry_call",
    "app.include_router": "router_mount",
    "register_blueprint": "blueprint_register",
}


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _file_type(path: Path) -> str:
    return path.suffix.lstrip(".") or "unknown"


def _resolve_import(
    module: str, current_file: Path, search_roots: List[Path]
) -> Optional[str]:
    """Resolve a Python import to an actual file path relative to a search root."""
    parts = module.split(".")
    for root in search_roots:
        for i in range(len(parts), 0, -1):
            pkg = parts[:i]
            remaining = parts[i:]
            # Check for package dir
            pkg_dir = root.joinpath(*pkg)
            if pkg_dir.is_dir() and (pkg_dir / "__init__.py").exists():
                if not remaining:
                    return str(pkg_dir / "__init__.py")
                file_path = pkg_dir.joinpath(*remaining).with_suffix(".py")
                if file_path.exists():
                    return str(file_path)
            # Check for single file
            file_path = root.joinpath(*parts).with_suffix(".py")
            if file_path.exists():
                return str(file_path)
    return None


class ASTScanner:
    def __init__(self, db: DepGraphDB, search_roots: Optional[List[Path]] = None):
        self.db = db
        self.search_roots = search_roots or []

    def scan_file(
        self, file_path: Path, force: bool = False
    ) -> Tuple[int, int, int]:
        """Scan a single file. Returns (import_count, export_count, edge_count).

        Skips if hash matches (unless force=True).
        """
        if not file_path.exists() or file_path.suffix != ".py":
            return (0, 0, 0)

        current_hash = _file_hash(file_path)
        if not force:
            existing = self.db._execute(
                "SELECT hash FROM files WHERE path = ?", (str(file_path),)
            ).fetchone()
            if existing and existing["hash"] == current_hash:
                return (0, 0, 0)

        path_str = str(file_path)
        ft = _file_type(file_path)

        self.db.remove_file(path_str)
        self.db.upsert_file(path_str, ft, current_hash)

        try:
            tree = ast.parse(file_path.read_text(), filename=path_str)
        except SyntaxError:
            return (0, 0, 0)

        imports: Set[str] = set()
        exports: List[Tuple[str, str, int]] = []

        for node in ast.iter_child_nodes(tree):
            # Regular imports: import foo, import foo.bar
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])

            # From imports: from foo import bar
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
                    for alias in node.names:
                        exports.append(
                            (alias.name, "import", alias.lineno or 0)
                        )

            # Function/class definitions (exports)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                exports.append((node.name, "function", node.lineno))
            elif isinstance(node, ast.ClassDef):
                exports.append((node.name, "class", node.lineno))

            # Decorators that register engines
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    decorator_name = _decorator_name(decorator)
                    if decorator_name in REGISTRY_PATTERNS:
                        edge_type = REGISTRY_PATTERNS[decorator_name]
                        self.db.add_edge(
                            path_str,
                            node.name,
                            edge_type=edge_type,
                            line_no=decorator.lineno,
                        )

            # Direct registry calls: orchestrator.register(MyEngine)
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                call_name = _call_name(call.func)
                if call_name:
                    for pattern, edge_type in REGISTRY_PATTERNS.items():
                        if call_name.endswith(pattern) or pattern in (call_name or ""):
                            for arg in call.args:
                                if isinstance(arg, ast.Name):
                                    self.db.add_edge(
                                        path_str,
                                        arg.id,
                                        edge_type=edge_type,
                                        line_no=call.lineno,
                                    )
                            break

        imp_count = 0
        for imp in imports:
            resolved = _resolve_import(imp, file_path, self.search_roots)
            if resolved:
                self.db.add_edge(path_str, resolved, edge_type="imports")
                imp_count += 1

        exp_count = 0
        for name, kind, line in exports:
            self.db.add_export(path_str, name, kind, line)
            exp_count += 1

        return (imp_count, exp_count, 0)

    def scan_directory(
        self, root: Path | str, pattern: str = "**/*.py", force: bool = False
    ) -> Dict[str, int]:
        """Scan an entire directory tree."""
        root = Path(root)
        start = time.time()
        total_imports = 0
        total_exports = 0
        total_edges = 0
        file_count = 0

        if not self.search_roots:
            self.search_roots = [root]

        for file_path in sorted(root.glob(pattern)):
            if file_path.name.startswith(".") or "venv" in file_path.parts or ".env" in file_path.parts:
                continue
            im, ex, ed = self.scan_file(file_path, force=force)
            total_imports += im
            total_exports += ex
            total_edges += ed
            file_count += 1

        duration_ms = (time.time() - start) * 1000
        self.db.log_scan(str(root), file_count, total_imports, duration_ms)

        return {
            "files": file_count,
            "imports": total_imports,
            "exports": total_exports,
            "edges": total_edges,
            "duration_ms": round(duration_ms, 2),
        }

    def scan_changed(self, root: Path | str) -> Dict[str, int]:
        """Incremental scan — only re-parse files whose hash changed."""
        root = Path(root)
        start = time.time()
        total_imports = 0
        total_exports = 0
        total_edges = 0
        file_count = 0

        for file_path in root.glob("**/*.py"):
            if file_path.name.startswith(".") or "venv" in file_path.parts:
                continue
            current_hash = _file_hash(file_path)
            existing = self.db._execute(
                "SELECT hash FROM files WHERE path = ?", (str(file_path),)
            ).fetchone()
            if existing and existing["hash"] == current_hash:
                continue
            im, ex, ed = self.scan_file(file_path, force=True)
            total_imports += im
            total_exports += ex
            total_edges += ed
            file_count += 1

        duration_ms = (time.time() - start) * 1000
        self.db.log_scan(str(root), file_count, total_imports, duration_ms)

        return {
            "files_changed": file_count,
            "imports": total_imports,
            "exports": total_exports,
            "edges": total_edges,
            "duration_ms": round(duration_ms, 2),
        }


def _decorator_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_decorator_name(node.value)}.{node.attr}" if node.value else node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return None


def _call_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _call_name(node.value)
        if base:
            return f"{base}.{node.attr}"
        return node.attr
    return None
