import json
from pathlib import Path
from typing import List

_TARGETS = {}

def load_targets():
    global _TARGETS
    # Try paths
    paths = [Path("data/extraction_targets.json"), Path("../../data/extraction_targets.json")]
    for p in paths:
        if p.exists():
            with open(p, "r") as f:
                _TARGETS = json.load(f)
            return

def get_targets_for_category(category: str) -> List[str]:
    if not _TARGETS:
        load_targets()
    category = category.lower() if category else "default"
    return _TARGETS.get(category, _TARGETS.get("default", []))
