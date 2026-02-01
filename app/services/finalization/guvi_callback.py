import httpx
from typing import Dict, Any, List
import logging
import settings

logger = logging.getLogger(__name__)

class GUVICallbackClient:
    
    @staticmethod
    async def send_final_result(
        session_id: str,
        scam_detected: bool,
        message_count: int,
        intel: Dict[str, Any],
        red_flags: List[str],
        notes: str
    ) -> bool:
        """
        Sends the mandatory final result to the GUVI evaluation endpoint.
        """
        
        # Map intel to required format
        formatted_intel = {
            "bankAccounts": intel.get("bank_account", []),
            "upiIds": intel.get("upi_id", []),
            "phishingLinks": intel.get("url", []),
            "phoneNumbers": intel.get("phone_number", []),
            "suspiciousKeywords": red_flags + intel.get("keywords", [])
        }
        
        payload = {
            "sessionId": session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": message_count,
            "extractedIntelligence": formatted_intel,
            "agentNotes": notes
        }
        
        # CRITICAL: Headers for authentication (Phase 8 requirement)
        headers = {
            "Content-Type": "application/json",
            "x-api-key": settings.GUVI_API_KEY or "DUMMY_KEY_FOR_TEST" 
        }
        
        url = settings.GUVI_CALLBACK_URL
        
        try:
            async with httpx.AsyncClient() as client:
                print(f"[GUVI Callback] Sending to {url}")
                print(f"[GUVI Callback] Headers: {headers}")
                print(f"[GUVI Callback] Payload: {payload}")
                
                response = await client.post(url, json=payload, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    print(f"[GUVI Callback] Success: {response.json()}")
                    return True
                else:
                    print(f"[GUVI Callback] Failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"[GUVI Callback] Error: {e}")
            return False
