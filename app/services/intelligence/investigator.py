"""
Investigator Agent — Extracts ALL intelligence from scammer conversations.

The LLM reads the FULL conversation and extracts every piece of suspicious
or identifying information the scammer has shared — nothing is skipped.
"""
from typing import Dict, List, Optional, Any
import json
import re

from app.services.llm.client import get_extraction_llm


class InvestigatorAgent:
    """
    Reads the entire conversation and extracts all data points the scammer
    revealed. Uses LLM with a detailed, open-ended extraction prompt.
    """

    SYSTEM_PROMPT = """You are a cyber intelligence analyst reviewing a conversation between a scammer and a victim.

YOUR JOB: Extract EVERY piece of identifying or suspicious information the SCAMMER has provided.
Think like a detective building a case file — capture anything that could identify the scammer
or prove the fraud: payment details, contact info, credentials, reference numbers, websites, anything.

=== WHAT TO EXTRACT ===

Go through the scammer's messages carefully and pull out:

1. upiIds
   Any UPI payment address (contains @ symbol used for sending money in India)
   UPI IDs end with bank/app handles like: @paytm, @ybl, @okaxis, @sbi, @hdfc, @icici, @okhdfcbank, @phonepe, @gpay
   e.g. name@paytm, number@ybl, refund@sbi, 9876543210@okaxis
   IMPORTANT: If someone says "send to xyz@sbi" or "pay to abc@paytm" - that's a UPI ID, not email!

2. phoneNumbers
   Any mobile/landline number the scammer gives for calls/WhatsApp/contact
   e.g. +91-9876543210, 9876543210
   Do NOT include numbers that are clearly amounts or account numbers.

3. bankAccounts
   Any bank account number the scammer shares for transfer
   e.g. 12345678901234 (typically 9-18 digits, given with bank name or IFSC)

4. bankNames
   Any bank or payment platform mentioned
   e.g. SBI, HDFC, ICICI, Paytm, PhonePe, Axis, Kotak

5. ifscCodes
   Any IFSC code (format: 4 letters + 0 + 6 alphanumeric)
   e.g. SBIN0001234, HDFC0004567

6. amounts
   Any monetary amount mentioned (just the number, no currency symbol)
   e.g. "5000", "299", "50000"
   Include even "processing fee", "security deposit", "verification charge" amounts.

7. phishingLinks
   Any URL or website link shared
   e.g. http://fake-bank.xyz, amaz0n-refund.com, bit.ly/scam123

8. emailAddresses
   Any email address shared (NOT UPI IDs!)
   Emails have domains like .com, .in, .org, .net, .xyz etc.
   e.g. support@fakesite.com, hr@company-name.in
   NOTE: xyz@sbi, abc@paytm are UPI IDs, not emails. Only put real email domains here.

9. caseIds
   Any reference number, case number, complaint number, FIR number,
   badge number, docket ID, ticket ID, or alphanumeric code the scammer
   uses to appear official or legitimate.
   e.g. CBI/2024/ML/4521, FIR-CRIME-789, KYC-REF-7821, CASE-12345
   Rule: If it's a code/ID the scammer cites as "proof" → extract here.

10. policyNumbers
    Any insurance policy number, government scheme number, plan ID,
    or registration number related to financial products.
    e.g. POL-12345, LIC/2024/789, PM-SCHEME-001

11. orderNumbers
    Any order ID, tracking number, shipment number, parcel reference,
    delivery AWB, or purchase reference code.
    e.g. ORD-789-2024, TRK-321, AMZ-FAKE-001, shipment #4521

=== HOW TO EXTRACT ===

- Read ALL scammer messages in the conversation carefully
- Extract from SCAMMER messages only — ignore victim responses
- If you see a number/ID — ask yourself: what is this person using it for?
  - Payment → upiId or bankAccount
  - Contact → phoneNumber
  - Proof of authority → caseId
  - Insurance/scheme → policyNumber
  - Order/delivery → orderNumber
  - Website → phishingLink
- Include partial or ambiguous items — lean toward extracting rather than skipping
- Deduplicate: don't list the same value twice in the same category
- Amounts: extract the numeric value only (e.g. "5000" not "Rs. 5000")

=== OUTPUT FORMAT ===

Return ONLY valid JSON. No markdown, no explanation, nothing else.

{
    "intelligence": {
        "upiIds": [],
        "phoneNumbers": [],
        "bankAccounts": [],
        "bankNames": [],
        "ifscCodes": [],
        "amounts": [],
        "phishingLinks": [],
        "emailAddresses": [],
        "caseIds": [],
        "policyNumbers": [],
        "orderNumbers": []
    },
    "agent_notes": "One sentence summary of what the scammer is trying to do",
    "confidence": 0.95
}

Empty arrays [] for categories with nothing to extract.
Confidence = how sure you are about the extraction quality (0.0 to 1.0)."""

    @classmethod
    async def analyze(cls, text: str, conversation_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyze a message and full conversation to extract all intelligence.
        Returns structured intel dict.
        """
        extraction_llm = get_extraction_llm()

        # Build full conversation context for the LLM
        conversation_context = cls._build_conversation_context(text, conversation_history)

        # Combine system prompt with task prompt
        prompt = f"""{cls.SYSTEM_PROMPT}

=== CONVERSATION TO ANALYZE ===
{conversation_context}

=== YOUR TASK ===
Extract every piece of identifying or suspicious information the scammer has shared.
Return ONLY valid JSON matching the format specified above. No markdown, no explanation."""

        try:
            response = extraction_llm.generate_json(prompt, temperature=0.1)

            if response and isinstance(response, dict):
                intel = response.get("intelligence", {})
                notes = response.get("agent_notes", "")
                confidence = response.get("confidence", 0.8)

                # Normalize all values to lists of strings
                normalized = cls._normalize_intel(intel)
                print(f"[Investigator] Extracted: {[k for k,v in normalized.items() if v]}")
                return {**normalized, "_notes": notes, "_confidence": confidence}

        except Exception as e:
            print(f"[Investigator] LLM extraction failed: {e}")

        return cls._empty_intel()

    @classmethod
    def _build_conversation_context(cls, latest_message: str, history: Optional[List[Dict]]) -> str:
        """Format full conversation for the LLM."""
        lines = []
        if history:
            for msg in history:
                role = msg.get("role", "user")
                sender = msg.get("sender", role)
                content = msg.get("content", "")
                if "user" in sender or "user" in role:
                    lines.append(f"SCAMMER: {content}")
                else:
                    lines.append(f"VICTIM: {content}")

        lines.append(f"SCAMMER: {latest_message}")
        return "\n".join(lines) if lines else f"SCAMMER: {latest_message}"

    @classmethod
    def _normalize_intel(cls, intel: Dict) -> Dict[str, List[str]]:
        """Ensure all fields are lists of clean strings."""
        fields = [
            "upiIds", "phoneNumbers", "bankAccounts", "bankNames",
            "ifscCodes", "amounts", "phishingLinks", "emailAddresses",
            "caseIds", "policyNumbers", "orderNumbers"
        ]
        result = {}
        for field in fields:
            raw = intel.get(field, [])
            if isinstance(raw, list):
                result[field] = [str(v).strip() for v in raw if v]
            elif raw:
                result[field] = [str(raw).strip()]
            else:
                result[field] = []
        return result

    @classmethod
    def _empty_intel(cls) -> Dict[str, List]:
        return {
            "upiIds": [], "phoneNumbers": [], "bankAccounts": [],
            "bankNames": [], "ifscCodes": [], "amounts": [],
            "phishingLinks": [], "emailAddresses": [],
            "caseIds": [], "policyNumbers": [], "orderNumbers": [],
            "_notes": "", "_confidence": 0.0
        }

    @classmethod
    def merge_intel(cls, existing: Dict, new_intel: Dict) -> Dict:
        """Merge new intel into existing, deduplicating all lists."""
        merged = dict(existing)
        list_fields = [
            "upiIds", "phoneNumbers", "bankAccounts", "bankNames",
            "ifscCodes", "amounts", "phishingLinks", "emailAddresses",
            "caseIds", "policyNumbers", "orderNumbers"
        ]
        for field in list_fields:
            existing_vals = set(merged.get(field, []))
            new_vals = new_intel.get(field, [])
            for v in new_vals:
                existing_vals.add(v)
            merged[field] = list(existing_vals)
        return merged
