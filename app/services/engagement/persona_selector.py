import json
from pathlib import Path
from typing import Dict, Optional

class PersonaSelector:
    _personas: Dict[str, Dict] = {}
    _loaded = False

    @classmethod
    def _load_personas(cls):
        if cls._loaded:
            return
            
        try:
            # Assuming running from root, adjust path if needed
            data_path = Path("data/personas.json")
            if not data_path.exists():
                # Fallback path if running from app subdirectory
                data_path = Path("../../data/personas.json")
            
            if data_path.exists():
                with open(data_path, "r", encoding="utf-8") as f:
                    cls._personas = json.load(f)
                cls._loaded = True
            else:
                print(f"Warning: Personas file not found at {data_path}")
        except Exception as e:
            print(f"Error loading personas: {e}")

    @classmethod
    def select_persona(cls, category: str) -> Dict[str, str]:
        """
        Selects a persona payload based on the detected scam category.
        Returns the persona dictionary (name, traits, style, etc.).
        """
        cls._load_personas()
        
        # Normalize category to lowercase
        category = category.lower() if category else "default"
        
        return cls._personas.get(category, cls._personas.get("default", {
            "name": "confused_user",
            "traits": "Uncertain, caution", 
            "style": "Simple questions"
        }))

    @classmethod
    def get_persona_name(cls, category: str) -> str:
        persona = cls.select_persona(category)
        return persona.get("name", "confused_user")
