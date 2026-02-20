"""
GUVI-Style Evaluation Test Suite
=================================
Simulates the GUVI evaluation exactly:
- AI-powered dynamic scammer (separate API key)
- 5 scam scenarios with planted intel
- Scores using GUVI's exact rubric
- Produces per-scenario + final score report

Usage:
    SCAMMER_API_KEY=sk-... python tests/guvi_eval_test.py
    SCAMMER_API_KEY=sk-... HONEYPOT_URL=https://your-space.hf.space python tests/guvi_eval_test.py
"""

import asyncio
import httpx
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

# Force UTF-8 on Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
HONEYPOT_URL   = os.getenv("HONEYPOT_URL",   "http://localhost:7860")
HONEYPOT_KEY   = os.getenv("HONEYPOT_API_KEY", "dev-key-123")
SCAMMER_KEY    = os.getenv("SCAMMER_API_KEY",  "")
SCAMMER_MODEL  = os.getenv("SCAMMER_MODEL",    "")   # auto-detected if blank
MAX_TURNS      = 5
REQUEST_TIMEOUT = 35

ENDPOINT = f"{HONEYPOT_URL}/api/message"

def _detect_provider(api_key: str, model_override: str) -> tuple[str, str]:
    """Auto-detect provider from key prefix and return (base_url, model)."""
    if api_key.startswith("gsk_"):
        return (
            "https://api.groq.com/openai/v1",
            model_override or "llama-3.3-70b-versatile"
        )
    # OpenRouter
    if api_key.startswith("sk-or-"):
        return (
            "https://openrouter.ai/api/v1",
            model_override or "google/gemini-2.0-flash-001"
        )
    # OpenAI
    return (
        "https://api.openai.com/v1",
        model_override or "gpt-4o-mini"
    )


# ─────────────────────────────────────────────
# 5 EVALUATION SCENARIOS  (weight sums to 100)
# ─────────────────────────────────────────────
# Each scenario has:
#   - planted_intel : ground truth the scammer WILL reveal if asked
#   - weight        : % of scenario score (like GUVI dynamic weights)
#   - scammer_system: persona/instructions for the scammer AI
# ─────────────────────────────────────────────

SCENARIOS = [
    {
        "id": "bank_fraud",
        "name": "Bank Fraud — SBI KYC",
        "weight": 25,
        "planted_intel": {
            "phoneNumbers":  ["+91-9876543210"],
            "upiIds":        ["refund.kyc@sbi"],
            "bankAccounts":  ["12345678901234"],
            "amounts":       ["5000"],
            "bankNames":     ["SBI"],
            "caseIds":       ["KYC-REF-2024-7821"],
        },
        "opening_message": (
            "Hello, I am calling from SBI customer care. "
            "Your KYC is expired and your account will be blocked in 24 hours. "
            "You need to update it immediately."
        ),
        "scammer_system": (
            "You are a scammer pretending to be an SBI bank employee doing KYC verification. "
            "Your goal is to extract money and personal details from the victim. "
            "You have the following fake details to share ONLY when specifically asked:\n"
            "- Your callback number: +91-9876543210\n"
            "- UPI ID to receive 'processing fee': refund.kyc@sbi\n"
            "- Bank account number: 12345678901234\n"
            "- Amount needed: Rs 5000 processing fee\n"
            "- Bank: SBI\n"
            "- Your case reference ID: KYC-REF-2024-7821\n"
            "Be convincing. Create urgency. Threaten account block. "
            "If asked for credentials, provide the fake ones above naturally. "
            "Keep messages short (1-3 sentences). Stay in character."
        ),
    },
    {
        "id": "digital_arrest",
        "name": "Digital Arrest — CBI Officer",
        "weight": 25,
        "planted_intel": {
            "phoneNumbers": ["+91-8765432100"],
            "caseIds":      ["CBI/2024/ML/4521", "FIR-CRIME-789"],
            "amounts":      ["50000"],
        },
        "opening_message": (
            "I am Deputy Superintendent Rajesh Kumar from CBI Cyber Crime division. "
            "Your Aadhar has been used for illegal Bitcoin transactions. "
            "You are under digital arrest."
        ),
        "scammer_system": (
            "You are a scammer impersonating a CBI officer. "
            "Fake details to provide when asked:\n"
            "- Your phone: +91-8765432100\n"
            "- Your case ID: CBI/2024/ML/4521\n"
            "- Related FIR: FIR-CRIME-789\n"
            "- Amount at stake: 50000\n"
            "Sound official. Add urgency and threat. Quote laws and procedures. "
            "Demand immediate action to 'secure' their account. Keep short."
        ),
    },
    {
        "id": "job_fraud",
        "name": "Job Fraud — Fake HR Recruiter",
        "weight": 20,
        "planted_intel": {
            "phoneNumbers":   ["+91-7654321098"],
            "emailAddresses": ["hr.fake@globaltech-india.com"],
            "upiIds":         ["training.fee@phonepe"],
            "amounts":        ["2500"],
            "phishingLinks":  ["http://globaltech-india-jobs.xyz/apply"],
        },
        "opening_message": (
            "Congratulations! Your profile has been selected for a Work From Home job. "
            "You can earn Rs 2500/day. Are you interested?"
        ),
        "scammer_system": (
            "You are a scammer recruiting for a fake job. Be enthusiastic! "
            "When asked, share:\n"
            "- HR contact: +91-7654321098\n"
            "- HR email: hr.fake@globaltech-india.com\n"
            "- Training UPI: training.fee@phonepe\n"
            "- Training fee: 2500\n"
            "- Application link: http://globaltech-india-jobs.xyz/apply\n"
            "Sound friendly and encouraging. Offer flexibility and high pay. "
            "Mention registration/training fee as 'company policy'."
        ),
    },
    {
        "id": "upi_fraud",
        "name": "UPI Cashback Scam",
        "weight": 15,
        "planted_intel": {
            "upiIds":       ["cashback.paytm2024@ybl"],
            "amounts":      ["299"],
            "phoneNumbers": ["+91-6543210987"],
        },
        "opening_message": (
            "Hi! You have won a special cashback of Rs 5000 from Paytm. "
            "To claim it, you just need to send Rs 299 for verification."
        ),
        "scammer_system": (
            "You are a scammer running a fake cashback scheme on Paytm. "
            "Details to provide:\n"
            "- Paytm UPI for sending verification: cashback.paytm2024@ybl\n"
            "- Verification amount: 299\n"
            "- Support phone: +91-6543210987\n"
            "Sound like official Paytm. Emphasize limited time. "
            "Make the verification step seem legitimate. Be persistent."
        ),
    },
    {
        "id": "phishing",
        "name": "Phishing — Amazon Order Scam",
        "weight": 15,
        "planted_intel": {
            "phishingLinks":  ["http://amaz0n-refund.xyz/claim?id=ORD789"],
            "emailAddresses": ["support@amaz0n-refund.xyz"],
            "orderNumbers":   ["ORD-789-2024-FAKE"],
            "amounts":        ["1299"],
        },
        "opening_message": (
            "Dear customer, your Amazon order #ORD-789-2024-FAKE worth Rs 1299 has been cancelled. "
            "Click here to claim your refund."
        ),
        "scammer_system": (
            "You are a scammer impersonating Amazon customer support to phish the victim. "
            "Goal: get the victim to click your link and enter payment info. "
            "Fake details to share when prompted:\n"
            "- Phishing link: http://amaz0n-refund.xyz/claim?id=ORD789\n"
            "- Fake support email: support@amaz0n-refund.xyz\n"
            "- Fake order number: ORD-789-2024-FAKE\n"
            "- Refund amount: Rs 1299\n"
            "Sound like official Amazon support. Create urgency about the refund expiring. "
            "Repeat the link if asked. Keep responses short and official-sounding."
        ),
    },
]


# ─────────────────────────────────────────────
# SCAMMER AI CLIENT
# ─────────────────────────────────────────────

async def scammer_respond(
    system_prompt: str,
    conversation: list[dict],
    api_key: str,
    model: str = ""
) -> str:
    """Use OpenAI-compatible API to generate scammer's next message."""
    if not api_key:
        raise ValueError("SCAMMER_API_KEY not set.")

    base_url, resolved_model = _detect_provider(api_key, model)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": resolved_model,
        "messages": [{"role": "system", "content": system_prompt}] + conversation,
        "temperature": 0.8,
        "max_tokens": 200,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()


# ─────────────────────────────────────────────
# HONEYPOT API CALLER
# ─────────────────────────────────────────────

async def call_honeypot(
    session_id: str,
    message_text: str,
    conversation_history: list,
    api_key: str
) -> dict:
    """Send a message to our honeypot API."""
    payload = {
        "sessionId": session_id,
        "message": {
            "text": message_text,
            "sender": "user",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": conversation_history,
        "metadata": {}
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        start = time.time()
        resp = await client.post(ENDPOINT, headers=headers, json=payload)
        elapsed = time.time() - start
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}: {resp.text}", "latency": elapsed}
        data = resp.json()
        data["_latency"] = round(elapsed, 2)
        return data


# ─────────────────────────────────────────────
# GUVI SCORER
# ─────────────────────────────────────────────

@dataclass
class ScenarioScore:
    scenario_id: str
    scenario_name: str
    weight: int

    # Component scores
    scam_detection: float = 0      # /20
    intelligence:   float = 0      # /30
    conv_quality:   float = 0      # /30
    engagement:     float = 0      # /10
    response_struct: float = 0     # /10

    # Details
    turns_completed: int = 0
    avg_latency: float = 0.0
    questions_asked: int = 0
    investigative_questions: int = 0
    red_flags_in_notes: int = 0
    extracted_items: list = field(default_factory=list)
    missed_items: list = field(default_factory=list)

    @property
    def total(self) -> float:
        return round(
            self.scam_detection +
            self.intelligence +
            self.conv_quality +
            self.engagement +
            self.response_struct, 1
        )


def score_scam_detection(detected: bool) -> float:
    """Scam Detection — 20pts."""
    return 20.0 if detected else 0.0


def score_intelligence_extraction(
    all_planted: dict,
    all_extracted: dict,
) -> tuple[float, list, list]:
    """Intelligence — 30pts (weighted by accuracy)."""
    CAT_MAP = {
        "bankAccounts": ["bankAccounts"],
        "upiIds": ["upiIds"],
        "phishingLinks": ["phishingLinks"],
        "phoneNumbers": ["phoneNumbers"],
        "suspiciousKeywords": ["suspiciousKeywords"],
        "amounts": ["amounts"],
        "bankNames": ["bankNames"],
        "ifscCodes": ["ifscCodes"],
        "emailAddresses": ["emailAddresses"],
        "caseIds": ["caseIds"],
        "policyNumbers": ["policyNumbers"],
        "orderNumbers": ["orderNumbers"],
    }

    found = []
    missed = []
    for category, value in all_planted.items():
        if not isinstance(value, list):
            value = [value]
        for v in value:
            extracted_list = []
            for mapped_cat in CAT_MAP.get(category, [category]):
                extracted_list.extend(all_extracted.get(mapped_cat, []))
            # Fuzzy match — check if planted value is substring of any extracted
            match = any(str(v).lower() in str(ex).lower() or str(ex).lower() in str(v).lower() for ex in extracted_list)
            if match:
                found.append(f"{category}:{v}")
            else:
                missed.append(f"{category}:{v}")

    all_planted_items = sum(len(v) if isinstance(v, list) else 1 for v in all_planted.values())
    ratio = len(found) / all_planted_items if all_planted_items > 0 else 0
    score = round(30 * ratio, 1)
    return score, found, missed


def count_questions(text: str) -> int:
    """Count question marks as proxy for questions asked."""
    return text.count("?")


def count_investigative_questions(reply: str) -> int:
    """Count questions about identity, organization, credentials."""
    keywords = [
        "who are you", "your name", "which department", "badge", "employee id",
        "case id", "case number", "your number", "office", "address", "website",
        "organization", "company", "verify", "senior officer", "designation",
        "which branch", "call back", "helpline", "department"
    ]
    reply_lower = reply.lower()
    return sum(1 for kw in keywords if kw in reply_lower and "?" in reply_lower)


def count_red_flags_in_notes(notes: str) -> int:
    """Estimate red flag count from agentNotes."""
    if not notes:
        return 0
    # Count semicolons as separator proxy, plus at least 1 if "red flags" mentioned
    if "red flag" in notes.lower():
        return max(1, notes.lower().count(";") + 1)
    return 0


def score_conversation_quality(
    responses: list[dict],
    turn_count: int
) -> tuple[float, int, int, int]:
    """Conversation Quality — 30pts."""
    score = 0.0

    # Turn count (max 8pts)
    if turn_count >= 8:
        score += 8
    elif turn_count >= 5:
        score += 5
    elif turn_count >= 3:
        score += 2

    # Count questions and investigative questions across all replies
    total_questions = 0
    total_investigative = 0
    for r in responses:
        reply = r.get("reply") or ""
        total_questions += count_questions(reply)
        total_investigative += count_investigative_questions(reply)

    # Questions asked (max 4pts)
    if total_questions >= 5:
        score += 4
    elif total_questions >= 3:
        score += 2
    elif total_questions >= 1:
        score += 1

    # Investigative questions (max 3pts)
    if total_investigative >= 3:
        score += 3
    elif total_investigative >= 2:
        score += 2
    elif total_investigative >= 1:
        score += 1

    # Red flags in agentNotes (max 8pts)
    max_red_flags = 0
    for r in responses:
        notes = r.get("agentNotes", "")
        rf = count_red_flags_in_notes(notes)
        max_red_flags = max(max_red_flags, rf)
    if max_red_flags >= 5:
        score += 8
    elif max_red_flags >= 3:
        score += 5
    elif max_red_flags >= 1:
        score += 2

    # Info elicitation (max 7pts — 1.5 per attempt)
    elicitation_score = min(7.0, total_investigative * 1.5)
    score += elicitation_score

    return min(30.0, round(score, 1)), total_questions, total_investigative, max_red_flags


def score_engagement_quality(
    final_response: dict,
    start_time: float,
    end_time: float
) -> float:
    """Engagement Quality — 10pts."""
    score = 0.0
    duration = end_time - start_time
    messages = final_response.get("totalMessagesExchanged", 0) or \
               final_response.get("engagementMetrics", {}).get("totalMessagesExchanged", 0)

    # Duration
    if duration > 0:
        score += 1
    if duration > 60:
        score += 2
    if duration > 180:
        score += 1

    # Messages
    if messages > 0:
        score += 2
    if messages >= 5:
        score += 3
    if messages >= 10:
        score += 1

    return min(10.0, score)


# ─────────────────────────────────────────────
# SINGLE SCENARIO RUNNER
# ─────────────────────────────────────────────

async def run_scenario(scenario: dict) -> ScenarioScore:
    session_id = f"eval-{scenario['id']}-{uuid.uuid4().hex[:8]}"
    result = ScenarioScore(
        scenario_id=scenario["id"],
        scenario_name=scenario["name"],
        weight=scenario["weight"]
    )

    print(f"\n{'='*60}")
    print(f"  SCENARIO: {scenario['name']}")
    print(f"  Session: {session_id}")
    print(f"{'='*60}")

    responses: list[dict] = []
    scammer_conversation: list[dict] = []  # for scammer AI
    honeypot_history: list[dict] = []      # for honeypot API
    latencies: list[float] = []

    start_time = time.time()
    current_scammer_msg = scenario["opening_message"]

    for turn in range(1, MAX_TURNS + 1):
        print(f"\n  [Turn {turn}] Scammer: {current_scammer_msg[:80]}...")

        # Call honeypot
        hp_response = await call_honeypot(
            session_id=session_id,
            message_text=current_scammer_msg,
            conversation_history=honeypot_history,
            api_key=HONEYPOT_KEY
        )

        if "error" in hp_response:
            print(f"  [ERROR] Honeypot failed: {hp_response['error']}")
            break

        latencies.append(hp_response.get("_latency", 0))
        responses.append(hp_response)

        reply = hp_response.get("reply") or ""
        detected = hp_response.get("scamDetected", False)
        print(f"  [Turn {turn}] Honeypot reply: {reply[:80]}...")
        print(f"             Detected={detected} | Latency={hp_response['_latency']}s")

        # Update honeypot history
        honeypot_history.append({"role": "user", "content": current_scammer_msg, "sender": "user"})
        honeypot_history.append({"role": "assistant", "content": reply, "sender": "assistant"})

        # Update scammer AI conversation
        scammer_conversation.append({"role": "assistant", "content": current_scammer_msg})
        scammer_conversation.append({"role": "user", "content": reply})

        # Generate next scammer message
        if turn < MAX_TURNS:
            try:
                current_scammer_msg = await scammer_respond(
                    system_prompt=scenario["scammer_system"],
                    conversation=scammer_conversation,
                    api_key=SCAMMER_KEY,
                    model=SCAMMER_MODEL
                )
            except Exception as e:
                print(f"  [WARN] Scammer AI error: {e}")
                break

    end_time = time.time()

    # Score this scenario
    result.turns_completed = len(responses)
    result.avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0

    # 1. Scam Detection
    result.scam_detection = score_scam_detection(
        responses[-1].get("scamDetected", False) if responses else False
    )

    # 2. Intelligence
    extracted_intel = {}
    for r in responses:
        intel = r.get("extractedIntelligence", {})
        for key, val in intel.items():
            if isinstance(val, list):
                extracted_intel.setdefault(key, []).extend(val)
            else:
                extracted_intel.setdefault(key, []).append(val)

    result.intelligence, result.extracted_items, result.missed_items = score_intelligence_extraction(
        scenario["planted_intel"],
        extracted_intel
    )

    # 3. Conversation Quality
    result.conv_quality, result.questions_asked, result.investigative_questions, result.red_flags_in_notes = \
        score_conversation_quality(responses, result.turns_completed)

    # 4. Engagement Quality
    result.engagement = score_engagement_quality(
        responses[-1] if responses else {},
        start_time,
        end_time
    )

    # 5. Response Structure
    result.response_struct = 10.0 if responses else 0.0

    return result


# ─────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────

async def main():
    # Header
    print("\n" + "=" * 60)
    print("GUVI HONEYPOT EVALUATION TEST SUITE")
    print("=" * 60)

    if not SCAMMER_KEY:
        print("ERROR: SCAMMER_API_KEY not set.")
        print("Usage: SCAMMER_API_KEY=gsk_... python tests/guvi_eval_test.py")
        sys.exit(1)

    print(f"Honeypot URL  : {HONEYPOT_URL}")
    base_url, model = _detect_provider(SCAMMER_KEY, SCAMMER_MODEL)
    print(f"Scammer AI    : {model}  ({base_url.split('/')[2]})")
    print(f"Scenarios     : {len(SCENARIOS)}")
    print(f"Turns / run   : {MAX_TURNS}")
    print()

    # Run scenarios
    all_results: list[ScenarioScore] = []
    for scenario in SCENARIOS:
        result = await run_scenario(scenario)
        all_results.append(result)

    # Compute final scores
    weighted_sum = sum(r.total * r.weight / 100 for r in all_results)
    scenario_portion = weighted_sum * 0.9
    code_quality = 8.0
    final_score = scenario_portion + code_quality

    # Print report header
    print("\n" + "=" * 70)
    print("  GUVI EVALUATION REPORT")
    print("=" * 70)

    # Scenario table
    print(f"\n{'Scenario':<30} {'Det':>5} {'Intel':>6} {'Conv':>5} {'Eng':>4} {'Struct':>6} {'Total':>6} {'Wt':>4} {'Contrib':>8}")
    print("-" * 70)
    for r in all_results:
        print(
            f"{r.scenario_name:<30} "
            f"{r.scam_detection:>5.1f} "
            f"{r.intelligence:>6.1f} "
            f"{r.conv_quality:>5.1f} "
            f"{r.engagement:>4.1f} "
            f"{r.response_struct:>6.1f} "
            f"{r.total:>6.1f} "
            f"{r.weight:>3}% "
            f"{r.total * r.weight / 100:>8.2f}"
        )
    print("-" * 70)
    print(f"{'Weighted Scenario Score':<58} {weighted_sum:>11.2f}")

    # Final calculation
    print("\n  Scenario Portion  (x0.9): {:.2f}".format(scenario_portion))
    print(f"  Code Quality (assumed)  : {code_quality:.1f}/10")
    print(f"  {'-' * 37}")
    print(f"  ESTIMATED FINAL SCORE   : {final_score:.1f}/100")

    # Detailed breakdown
    print("\n" + "=" * 70)
    print("  SCENARIO BREAKDOWN")
    print("=" * 70)

    for r in all_results:
        print(f"\n  [{r.scenario_name}]")
        print(f"    Turns completed : {r.turns_completed}/{MAX_TURNS}")
        print(f"    Avg latency     : {r.avg_latency}s")
        print(f"    Questions asked : {r.questions_asked}")
        print(f"    Investigative Q : {r.investigative_questions}")
        print(f"    Red flags noted : {r.red_flags_in_notes}")
        print(f"    Intel extracted : {r.extracted_items}")
        print(f"    Intel missed    : {r.missed_items}")
        print(f"    Score           : {r.total:.1f}/100")

    # Save report
    report_path = "tests/eval_report.json"
    report_data = {
        "final_score_estimate": round(final_score, 2),
        "weighted_scenario_score": round(weighted_sum, 2),
        "scenarios": [
            {
                "id": r.scenario_id,
                "name": r.scenario_name,
                "weight": r.weight,
                "scam_detection": r.scam_detection,
                "intelligence": r.intelligence,
                "conv_quality": r.conv_quality,
                "engagement": r.engagement,
                "response_struct": r.response_struct,
                "total": r.total,
                "turns_completed": r.turns_completed,
                "avg_latency": r.avg_latency,
                "questions_asked": r.questions_asked,
                "investigative_questions": r.investigative_questions,
                "red_flags_in_notes": r.red_flags_in_notes,
                "extracted_items": r.extracted_items,
                "missed_items": r.missed_items,
            }
            for r in all_results
        ]
    }
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n  Full report saved to: {report_path}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
