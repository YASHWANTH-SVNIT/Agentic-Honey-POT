import json
from pathlib import Path

PERSONAS = {}

# Load personas from JSON
data_path = Path(__file__).parent.parent / "data" / "personas.json"
if data_path.exists():
    with open(data_path, "r", encoding="utf-8") as f:
        PERSONAS = json.load(f)
else:
    print(f"Warning: Personas file not found at {data_path}")
