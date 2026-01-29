import json
from pathlib import Path

STAGES = {}

# Load stages from JSON
data_path = Path(__file__).parent.parent / "data" / "stage_config.json"
if data_path.exists():
    with open(data_path, "r", encoding="utf-8") as f:
        STAGES = json.load(f)
else:
    print(f"Warning: Stages file not found at {data_path}")
