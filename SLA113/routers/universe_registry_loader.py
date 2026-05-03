"""
universe_registry_loader.py — loads SHARED/universe_registry.yaml at runtime
for use by SLA113 kernel and routers.
"""
from pathlib import Path
import yaml


def load_registry() -> dict:
    registry_path = Path(__file__).resolve().parents[3] / "SHARED" / "universe_registry.yaml"
    with open(registry_path, "r") as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    import json
    reg = load_registry()
    print(json.dumps(list(reg.get("universes", {}).keys()), indent=2))
