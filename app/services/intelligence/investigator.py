"""
AI-Powered Intelligence Investigator
Replaces regex-based extraction with context-aware LLM extraction
No more collisions between phone numbers and bank accounts!
"""
from typing import Dict, Any, List, Optional
import json
import re
from app.services.llm.client import get_llm_client

class InvestigatorAgent:
    """
    Specialized AI agent for extracting actionable intelligence from scammer messages.
    Uses LLM with structured prompts to avoid regex collisions.
    """
    
    SYSTEM_PROMPT = """You are a cyber intelligence analyst extracting payment and contact information from scammer messages.

EXTRACTION CATEGORIES:

1. **upiIds**: Payment identifiers with @ symbol
   Format: username@provider (e.g., scammer@paytm, number@ybl)

2. **phoneNumbers**: 10-digit Indian mobile numbers in calling/messaging context
   Context keywords: "call", "contact", "message", "WhatsApp", "SMS"
   Disambiguation: If number appears with payment context, it's NOT a phone number

3. **bankAccounts**: 9-18 digit numbers in payment/transfer context
   Context keywords: "account", "transfer", "deposit", "A/c", "send to"
   Disambiguation: Use context to distinguish from phone numbers

4. **amounts**: Monetary values mentioned
   Formats: ₹50000, Rs 5000, rupees, thousand, lakh
   Extract as numeric string only (e.g., "50000")

5. **bankNames**: Financial institutions mentioned
   Examples: SBI, HDFC, ICICI, Paytm, PhonePe, Axis, Kotak, PNB
   Include abbreviations and full names

6. **ifscCodes**: Bank branch identifiers
   Format: 4 letters + "0" + 6 alphanumeric (e.g., SBIN0001234)

7. **phishingLinks**: URLs or domains
   Formats: https://site.com, www.site.com, bit.ly/xyz

8. **emailIds**: Email addresses mentioned
   Format: name@domain.com (e.g., hr@company.com, support@gmail.com)

DISAMBIGUATION RULES:
- If number with "call/contact/message" → phoneNumber
- If number with "account/transfer/pay" → bankAccount  
- If number has @ symbol → upiId
- Same number can be BOTH if in different contexts

OUTPUT FORMAT (JSON ONLY):
{
    "intelligence": {
        "upiIds": [],
        "phoneNumbers": [],
        "bankAccounts": [],
        "amounts": [],
        "bankNames": [],
        "ifscCodes": [],
        "phishingLinks": [],
        "emailIds": []
    },
    "agent_notes": "Brief summary of scammer request",
    "confidence": 0.0-1.0
}

INSTRUCTIONS:
- Extract ALL relevant information
- Use conversation history for context
- Resolve ambiguities intelligently
- Return ONLY valid JSON (no markdown, no explanations)
- Empty arrays [] if category not found
- Calculate confidence based on extraction clarity"""

    @classmethod
    async def analyze(cls, text: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyzes scammer message to extract actionable intelligence.
        
        Args:
            text: Current scammer message
            conversation_history: Previous messages for context
            
        Returns:
            Dict with intelligence, agent_notes, and confidence
        """
        if not text or len(text.strip()) < 3:
            return cls._get_empty_result("Message too short or empty")
            
        try:
            client = get_llm_client()
            
            # Build context from conversation history (last 3 messages)
            context = ""
            if conversation_history:
                recent = conversation_history[-3:]
                context_lines = []
                for msg in recent:
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    context_lines.append(f"{role}: {content}")
                context = "CONVERSATION CONTEXT:\n" + "\n".join(context_lines) + "\n\n"
            
            # Construct user prompt
            user_prompt = f"""{context}CURRENT SCAMMER MESSAGE:
"{text}"

Extract all intelligence and return ONLY the JSON format specified above."""
            
            # Call LLM with low temperature for precision
            full_prompt = f"{cls.SYSTEM_PROMPT}\n\n{user_prompt}"
            
            print(f"[InvestigatorAgent] Analyzing message...")
            raw_response = client.generate(full_prompt, temperature=0.1, max_tokens=500)
            print(f"[InvestigatorAgent] LLM Response received")
            
            # Parse response
            result = cls._parse_llm_response(raw_response, text)
            
            # Validate and clean
            result = cls._validate_and_clean(result, text)
            
            return result
            
        except Exception as e:
            print(f"[InvestigatorAgent] Extraction error: {e}")
            import traceback
            traceback.print_exc()
            return cls._get_empty_result(f"Extraction failed: {str(e)}")

    @staticmethod
    def _parse_llm_response(raw_response: str, original_text: str) -> Dict[str, Any]:
        """Parse LLM response, handling common formatting issues."""
        try:
            # Remove markdown code blocks
            cleaned = re.sub(r'```(?:json)?\s*', '', raw_response)
            cleaned = cleaned.strip()
            
            # Try to parse
            data = json.loads(cleaned)
            
            # Ensure required structure
            if "intelligence" not in data:
                # Try to find JSON object in response
                json_match = re.search(r'\{[\s\S]*\}', cleaned)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    raise ValueError("Missing 'intelligence' key in response")
                
            return data
            
        except json.JSONDecodeError as e:
            print(f"[InvestigatorAgent] JSON parse error: {e}")
            print(f"[InvestigatorAgent] Raw response: {raw_response[:500]}")
            
            # Attempt to extract JSON from malformed response
            try:
                json_match = re.search(r'\{[\s\S]*\}', raw_response)
                if json_match:
                    return json.loads(json_match.group())
            except:
                pass
                    
            return InvestigatorAgent._get_empty_result("JSON parsing failed")

    @staticmethod
    def _validate_and_clean(result: Dict[str, Any], original_text: str) -> Dict[str, Any]:
        """
        Validate and clean extracted intelligence.
        Removes duplicates and performs sanity checks.
        """
        intel = result.get("intelligence", {})
        
        # Ensure all expected keys exist
        required_keys = ["upiIds", "phoneNumbers", "bankAccounts", "amounts", 
                        "bankNames", "ifscCodes", "phishingLinks", "emailIds"]
        for key in required_keys:
            if key not in intel:
                intel[key] = []
        
        # Remove duplicates and clean
        for key in required_keys:
            if intel[key]:
                # Remove duplicates while preserving order
                intel[key] = list(dict.fromkeys(intel[key]))
                
                # Clean strings (remove extra whitespace)
                intel[key] = [str(item).strip() for item in intel[key] if item and str(item).strip()]
        
        # Validate UPI IDs (must contain @)
        intel["upiIds"] = [upi for upi in intel["upiIds"] if "@" in upi]
        
        # Validate phone numbers (10 digits starting with 6-9)
        validated_phones = []
        for phone in intel["phoneNumbers"]:
            # Extract digits only
            digits = re.sub(r'\D', '', phone)
            if re.match(r'^[6-9]\d{9}$', digits):
                validated_phones.append(digits)
        intel["phoneNumbers"] = validated_phones
        
        # Validate IFSC codes (4 letters + 0 + 6 alphanumeric)
        validated_ifsc = []
        for ifsc in intel["ifscCodes"]:
            ifsc_upper = ifsc.upper().strip()
            if re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_upper):
                validated_ifsc.append(ifsc_upper)
        intel["ifscCodes"] = validated_ifsc
        
        # Validate bank accounts (9-18 digits)
        validated_accounts = []
        for acc in intel["bankAccounts"]:
            digits = re.sub(r'\D', '', acc)
            if re.match(r'^\d{9,18}$', digits):
                validated_accounts.append(digits)
        intel["bankAccounts"] = validated_accounts
        
        # Clean amounts (extract numbers only)
        validated_amounts = []
        for amt in intel["amounts"]:
            digits = re.sub(r'[^\d]', '', str(amt))
            if digits:
                validated_amounts.append(digits)
        intel["amounts"] = validated_amounts
        
        # Validate URLs (must contain URL indicators)
        validated_links = []
        for link in intel["phishingLinks"]:
            link_lower = link.lower()
            if any(indicator in link_lower for indicator in ['http', 'www.', '.com', '.in', '.org', 'bit.ly', '.co']):
                validated_links.append(link)
        intel["phishingLinks"] = validated_links
        
        # Validate email addresses
        validated_emails = []
        for email in intel["emailIds"]:
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                 validated_emails.append(email)
        intel["emailIds"] = validated_emails
        
        # Update result
        result["intelligence"] = intel
        
        # Ensure agent_notes exists
        if "agent_notes" not in result or not result["agent_notes"]:
            # Generate notes based on extracted data
            notes_parts = []
            if intel["upiIds"]:
                notes_parts.append(f"UPI payment requested")
            if intel["bankAccounts"]:
                notes_parts.append(f"Bank transfer requested")
            if intel["amounts"]:
                notes_parts.append(f"Amount: ₹{intel['amounts'][0]}")
            result["agent_notes"] = ". ".join(notes_parts) if notes_parts else "Intelligence extraction attempted"
            
        # Ensure confidence exists
        if "confidence" not in result or not isinstance(result.get("confidence"), (int, float)):
            # Calculate confidence based on extraction success
            found_items = sum(1 for v in intel.values() if v)
            result["confidence"] = min(0.95, 0.3 + (found_items * 0.1))
        
        return result

    @staticmethod
    def _get_empty_result(reason: str = "No intelligence found") -> Dict[str, Any]:
        """Return empty result structure."""
        return {
            "intelligence": {
                "upiIds": [],
                "phoneNumbers": [],
                "bankAccounts": [],
                "amounts": [],
                "bankNames": [],
                "ifscCodes": [],
                "phishingLinks": [],
                "emailIds": []
            },
            "agent_notes": reason,
            "confidence": 0.0
        }

    @staticmethod
    def merge_intelligence(existing: Dict, new: Dict) -> Dict:
        """
        Merge new intelligence into existing session intelligence.
        Removes duplicates across the entire session.
        """
        merged = existing.copy() if existing else {}
        
        # Ensure all keys exist in merged
        for key in ["upiIds", "phoneNumbers", "bankAccounts", "amounts", 
                   "bankNames", "ifscCodes", "phishingLinks", "emailIds"]:
            if key not in merged:
                merged[key] = []
        
        # Merge each category
        for key in ["upiIds", "phoneNumbers", "bankAccounts", "amounts", 
                   "bankNames", "ifscCodes", "phishingLinks", "emailIds"]:
            # Combine both lists
            combined = merged.get(key, []) + new.get(key, [])
            # Remove duplicates while preserving order
            merged[key] = list(dict.fromkeys(combined))
        
        return merged


# ============================================================
# Convenience Functions
# ============================================================

def get_investigator() -> InvestigatorAgent:
    """Get investigator class for use in other modules."""
    return InvestigatorAgent
