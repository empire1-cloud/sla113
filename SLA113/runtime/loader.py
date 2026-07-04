"""RuntimeLoader — hot-loads capability packs and registers their providers."""

from __future__ import annotations

import importlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from SLA113.execution_engine.provider import ProviderDef, ProviderRouter, ProviderType


class CapabilityPack:
    """A loaded capability pack with its providers and metadata."""

    def __init__(self, pack_path: Path):
        self.path = pack_path
        self.manifest: Dict[str, Any] = {}
        self.providers: List[ProviderDef] = []
        self._handlers: Dict[str, Callable] = {}
        self._loaded = False

    def load(self) -> bool:
        manifest_path = self.path / "pack.json"
        if not manifest_path.exists():
            return False

        with open(manifest_path) as f:
            self.manifest = json.load(f)

        providers_dir = self.path / "providers"
        if providers_dir.exists():
            for pfile in providers_dir.glob("*.json"):
                with open(pfile) as f:
                    pdata = json.load(f)
                    provider = ProviderDef(
                        id=pdata.get("id", pfile.stem),
                        name=pdata.get("name", pfile.stem),
                        provider_type=pdata.get("provider_type", ProviderType.LOCAL_DSP),
                        lifecycle=pdata.get("lifecycle", "active"),
                        priority=pdata.get("priority", 50),
                        cost_per_call=pdata.get("cost_per_call", 0.0),
                        latency_ms=pdata.get("latency_ms", 0),
                        config=pdata.get("config", {}),
                    )
                    self.providers.append(provider)

        impl_dir = self.path / "impl"
        if impl_dir.exists():
            for pyfile in impl_dir.glob("*.py"):
                module_name = f"_pack_{self.manifest.get('name', 'unknown')}_{pyfile.stem}"
                spec = importlib.util.spec_from_file_location(module_name, pyfile)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    for attr in dir(mod):
                        if attr.startswith("handle_"):
                            svc_id = attr.replace("handle_", "").replace("_", "-")
                            self._handlers[svc_id] = getattr(mod, attr)

        self._loaded = True
        return True

    def is_loaded(self) -> bool:
        return self._loaded

    def get_handler(self, provider_id: str) -> Optional[Callable]:
        return self._handlers.get(provider_id)

    def register_with(self, router: ProviderRouter):
        for p in self.providers:
            router.register(p, self._handlers.get(p.id, lambda *a, **kw: None))


class RuntimeLoader:
    """Loads capability packs from the filesystem and registers their providers."""

    def __init__(self, packs_root: Optional[str] = None):
        if packs_root is None:
            packs_root = str(
                Path(__file__).parent.parent / "universe_compiler" / "packs"
            )
        self.packs_root = Path(packs_root)
        self.packs: Dict[str, CapabilityPack] = {}

    def discover(self) -> List[str]:
        """Scan packs_root and return all pack directory names."""
        if not self.packs_root.exists():
            return []
        return [
            d.name
            for d in self.packs_root.iterdir()
            if d.is_dir() and (d / "pack.json").exists()
        ]

    def load_pack(self, pack_name: str) -> Optional[CapabilityPack]:
        pack_path = self.packs_root / pack_name
        if not pack_path.exists():
            return None
        pack = CapabilityPack(pack_path)
        if pack.load():
            self.packs[pack_name] = pack
            return pack
        return None

    def load_all(self) -> Dict[str, CapabilityPack]:
        for name in self.discover():
            self.load_pack(name)
        return self.packs

    def register_all(self, router: ProviderRouter):
        for pack in self.packs.values():
            pack.register_with(router)

    def get_pack(self, name: str) -> Optional[CapabilityPack]:
        return self.packs.get(name)

    def list_loaded(self) -> List[str]:
        return list(self.packs.keys())
