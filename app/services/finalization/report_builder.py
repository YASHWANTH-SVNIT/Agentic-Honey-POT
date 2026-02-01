from typing import Dict, Any, List
from app.models.session import SessionData
from datetime import datetime

class ReportBuilder:
    
    @staticmethod
    def build_final_report(session: SessionData) -> Dict[str, Any]:
        """
        Assembles a comprehensive final intelligence report for the session.
        Matches the rich Phase 7 documentation format.
        """
        
        # Calculate durations
        duration_seconds = int((datetime.now() - session.created_at).total_seconds())
        
        # Assemble Report
        report = {
            "sessionId": session.session_id,
            "scamDetected": session.scam_detected,
            "scamCategory": session.category,
            "scamType": session.scam_type,
            "detectionConfidence": session.confidence,
            "detectionMode": session.detection_mode or "N/A",
            "detectedLanguage": session.detected_language or "en",
            
            "usageMetrics": {
                "totalMessagesExchanged": session.turn_count * 2,
                "conversationDurationSeconds": duration_seconds
            },
            
            "extractedIntelligence": {
                "bankAccounts": session.extracted_intel.get("bank_account", []),
                "upiIds": session.extracted_intel.get("upi_id", []),
                "phishingLinks": session.extracted_intel.get("url", []),
                "phoneNumbers": session.extracted_intel.get("phone_number", []),
                "suspiciousKeywords": session.extracted_intel.get("keywords", []),
                "videoCallPlatforms": session.extracted_intel.get("video_platform", []),
                "meetingIds": session.extracted_intel.get("meeting_id", []),
                "caseNumbers": session.extracted_intel.get("case_number", []),
                "impersonatedAuthorities": session.extracted_intel.get("impersonated_authority", []),
                "fakeOfficerNames": session.extracted_intel.get("officer_name", [])
            },
            
            "conversationAnalysis": {
                "redFlags": session.red_flags,
                # Tactics could be inferred or added to session model later
                "tacticsUsed": ["Urgency", "Threats"] if session.scam_detected else [] 
            },
            
            "agentPerformance": {
                "personaUsed": session.persona,
                "stagesCompleted": getattr(session, "completed_stages", []) 
            },
            
            "agentNotes": f"Category: {session.category}. Reasoning: {session.reasoning}"
        }
        
        return report
