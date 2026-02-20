from typing import Dict, Any, List
from app.models.session import SessionData
from datetime import datetime

class ReportBuilder:
    
    @staticmethod
    def build_final_report(session: SessionData) -> Dict[str, Any]:
        """
        Assembles final intelligence report matching evaluation spec exactly.
        Returns only required fields as per evaluation criteria.
        """
        
        # Calculate durations
        duration_seconds = int((datetime.now() - session.created_at).total_seconds())
        total_messages = session.turn_count * 2
        
        # Assemble Report - EXACT evaluation format
        report = {
            "sessionId": session.session_id,
            "scamDetected": session.scam_detected,
            "totalMessagesExchanged": total_messages,
            "engagementDurationSeconds": duration_seconds,
            "extractedIntelligence": {
                "phoneNumbers": session.extracted_intel.get("phoneNumbers", []) or session.extracted_intel.get("phone_number", []),
                "bankAccounts": session.extracted_intel.get("bankAccounts", []) or session.extracted_intel.get("bank_account", []),
                "upiIds": session.extracted_intel.get("upiIds", []) or session.extracted_intel.get("upi_id", []),
                "phishingLinks": session.extracted_intel.get("phishingLinks", []) or session.extracted_intel.get("url", []),
                "emailAddresses": session.extracted_intel.get("emailAddresses", []) or session.extracted_intel.get("emailIds", []),
                "amounts": session.extracted_intel.get("amounts", []),
                "bankNames": session.extracted_intel.get("bankNames", []),
                "ifscCodes": session.extracted_intel.get("ifscCodes", [])
            },
            "agentNotes": f"Category: {session.category}. Type: {session.scam_type}. Reasoning: {session.reasoning or 'Scam detected and engaged'}"
        }
        
        return report
