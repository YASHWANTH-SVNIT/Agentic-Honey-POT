"""
Intelligence Extraction Service
Extracts UPI IDs, phone numbers, URLs, and other intelligence using regex
"""
import re
from typing import Dict, List, Any


class IntelligenceExtractor:
    """Extracts intelligence from scammer messages"""
    
    def __init__(self):
        """Initialize extraction patterns"""
        self.patterns = {
            "upi_ids": r'[\w\.\-]+@[\w]+',
            "phone_numbers": r'(?:\+91[\-\s]?)?[6-9]\d{9}',
            "urls": r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?',
            "bank_accounts": r'\b\d{9,18}\b',
            "ifsc_codes": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            "case_numbers": r'(?:Case|FIR|Ref|ID)[\s:]*[A-Z0-9\/\-]+',
            "meeting_ids": r'(?:Meeting\s+ID|ID)[\s:]*[\d\-]+',
        }
        
        self.keywords = [
            "urgent", "arrest", "police", "CBI", "ED", "income tax",
            "money laundering", "case", "investigation", "video call",
            "Zoom", "WhatsApp", "payment", "UPI", "bank", "account",
            "KYC", "expired", "blocked", "verify", "OTP", "CVV"
        ]
        
        print("✓ Intelligence extractor initialized")
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract all intelligence from text"""
        intel = {}
        
        # Extract using regex patterns
        for key, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Remove duplicates and clean
                intel[key] = list(set(match.strip() for match in matches))
        
        # Extract keywords
        found_keywords = []
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        if found_keywords:
            intel["keywords"] = list(set(found_keywords))
        
        # Extract video platforms
        video_platforms = []
        if re.search(r'\bzoom\b', text, re.IGNORECASE):
            video_platforms.append("Zoom")
        if re.search(r'\bwhatsapp\b', text, re.IGNORECASE):
            video_platforms.append("WhatsApp")
        if re.search(r'\bgoogle\s+meet\b', text, re.IGNORECASE):
            video_platforms.append("Google Meet")
        if re.search(r'\bteams\b', text, re.IGNORECASE):
            video_platforms.append("Microsoft Teams")
        
        if video_platforms:
            intel["video_platforms"] = video_platforms
        
        # Extract impersonated authorities
        authorities = []
        if re.search(r'\bCBI\b', text, re.IGNORECASE):
            authorities.append("CBI")
        if re.search(r'\bED\b|\bEnforcement\s+Directorate\b', text, re.IGNORECASE):
            authorities.append("Enforcement Directorate")
        if re.search(r'\bIncome\s+Tax\b', text, re.IGNORECASE):
            authorities.append("Income Tax Department")
        if re.search(r'\bPolice\b', text, re.IGNORECASE):
            authorities.append("Police")
        if re.search(r'\bNCB\b', text, re.IGNORECASE):
            authorities.append("NCB")
        
        if authorities:
            intel["impersonated_authorities"] = authorities
        
        return intel
    
    def merge_intelligence(self, existing: Dict[str, List[str]], new: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Merge new intelligence with existing"""
        merged = existing.copy()
        
        for key, values in new.items():
            if key in merged:
                # Merge and remove duplicates
                merged[key] = list(set(merged[key] + values))
            else:
                merged[key] = values
        
        return merged


# Global instance
_intelligence_extractor = None

def get_intelligence_extractor() -> IntelligenceExtractor:
    """Get or create global intelligence extractor instance"""
    global _intelligence_extractor
    if _intelligence_extractor is None:
        _intelligence_extractor = IntelligenceExtractor()
    return _intelligence_extractor
