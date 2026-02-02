import re
from typing import Dict, Any, List

class IntelExtractor:
    PATTERNS = {
        "upi_id": re.compile(r"[\w\.\-]+@[\w\.\-]+"),
        "phone_number": re.compile(r"(?:\+91|91)?\s?[6-9]\d{9}"),
        "url": re.compile(r"https?://[^\s]+"),
        "email": re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),
        "bank_account": re.compile(r"\b\d{9,20}\b"),
        "ifsc": re.compile(r"[A-Z]{4}0[A-Z0-9]{6}"),
        # Basic context keywords to capture surrounding info (simplified)
        "meeting_id": re.compile(r"(?:meeting|zoom|id)[:\s-]+(\d{3,}[-\s]?\d{3,}[-\s]?\d{3,})", re.IGNORECASE)
    }

    @classmethod
    def extract_all(cls, text: str) -> Dict[str, Any]:
        results = {}
        for key, pattern in cls.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                # Deduplicate and clean
                clean_matches = list(set([m.strip() if isinstance(m, str) else m for m in matches]))
                if clean_matches:
                    results[key] = clean_matches
        return results

    def extract(self, text: str) -> Dict[str, Any]:
        """Alias for extract_all to match test expectations"""
        return self.extract_all(text)

def get_intelligence_extractor():
    return IntelExtractor()
