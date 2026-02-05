"""
✅ MASTER SYSTEM TEST SUITE - ENHANCED VERSION
--------------------------
Comprehensive End-to-End Test for Agentic Honey-Pot.

NEW FEATURES:
- Conversation simulation (10-turn realistic scam)
- Extraction quality verification
- Response quality checks (casualness, typos, variation)
- Anti-repetition verification

Usage:
    python test_full_system.py
"""

import sys
import os
# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from datetime import datetime
import httpx
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(".")

# Import App
from main import app

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Initialize Test Client
client = TestClient(app)

# Global Test State
SESSION_ID = f"test-session-{int(datetime.now().timestamp())}"
HISTORY = []

def log_test(name, passed, details=""):
    status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
    print(f"[{status}] {name}")
    if details:
        print(f"       {details}")

def send_message(text, metadata=None):
    """Helper to send message via API"""
    payload = {
        "sessionId": SESSION_ID,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": HISTORY,
        "metadata": metadata
    }
    
    headers = {"x-api-key": "agentic_honey_pot_2026"}
    
    try:
        response = client.post("/api/message", json=payload, headers=headers)
        if response.status_code != 200:
            print(f"{RED}API Error: {response.status_code} - {response.text}{RESET}")
            return None
        
        data = response.json()
        
        # Update history
        HISTORY.append({"role": "user", "content": text})
        if data.get("reply"):
            HISTORY.append({"role": "assistant", "content": data["reply"]})
            
        return data
    except Exception as e:
        print(f"{RED}Client Error: {e}{RESET}")
        return None

def test_01_language_detection():
    print(f"\n{CYAN}🔍 TEST 1: LANGUAGE DETECTION{RESET}")
    print("-" * 50)
    
    # 1. Test English (should work)
    res = send_message("Hello", metadata={"language": "en"})
    passed = res and res.get("action") != "not_supported"
    log_test("English language accepted", passed, f"Action: {res.get('action') if res else 'None'}")
    
    # 2. Test French (should reject)
    res_fr = send_message("Bonjour monsieur", metadata={"language": "fr"})
    passed_fr = res_fr and res_fr.get("action") == "not_supported"
    log_test("French language rejected", passed_fr, f"Action: {res_fr.get('action') if res_fr else 'None'}")
    
    # 3. Test unknown (should accept - benefit of doubt)
    res_unknown = send_message("xyz abc", metadata={"language": "unknown"})
    passed_unknown = res_unknown and res_unknown.get("action") != "not_supported"
    log_test("Unknown language accepted (lenient)", passed_unknown)

def test_02_scam_detection():
    print(f"\n{CYAN}🛡️ TEST 2: SCAM DETECTION PIPELINE{RESET}")
    print("-" * 50)
    
    global SESSION_ID, HISTORY
    SESSION_ID = f"test-scam-{int(datetime.now().timestamp())}"
    HISTORY = []
    
    scam_text = "This is CBI Police. Your Aadhaar is misuse for money laundering. You are under digital arrest. Verify now immediately."
    res = send_message(scam_text, metadata={"language": "en"})
    
    if res:
        is_scam = res.get("scamDetected", False)
        log_test("Scam detected", is_scam, f"Confidence: {res.get('engagementMetrics', {})}")
        
        reply = res.get("reply", "")
        has_reply = len(reply) > 5
        log_test("Engagement triggered", has_reply, f"Reply: {reply[:70]}...")
        
        # Check if reply sounds casual
        casual_indicators = ["wat", "im", "scared", "oh", "umm", "ok"]
        is_casual = any(ind in reply.lower() for ind in casual_indicators)
        log_test("Response sounds casual", is_casual, "Contains casual language")

def test_03_ai_intelligence_extraction():
    print(f"\n{CYAN}🧠 TEST 3: AI INTELLIGENCE EXTRACTION{RESET}")
    print("-" * 50)
    
    # Send message with multiple intelligence types
    intel_text = "Transfer Rs 50000 to UPI police.verify@sbi or call 9876543210. Bank account 123456789012 at HDFC Bank IFSC HDFC0001234."
    res = send_message(intel_text, metadata={"language": "en"})
    
    if res:
        intel = res.get("extractedIntelligence", {})
        
        # Check UPI
        upis = intel.get("upiIds", [])
        has_upi = "police.verify@sbi" in str(upis)
        log_test("UPI ID extracted", has_upi, f"Found: {upis}")
        
        # Check Phone
        phones = intel.get("phoneNumbers", [])
        has_phone = "9876543210" in str(phones)
        log_test("Phone number extracted", has_phone, f"Found: {phones}")
        
        # Check Bank Account
        accounts = intel.get("bankAccounts", [])
        has_account = "123456789012" in str(accounts)
        log_test("Bank account extracted", has_account, f"Found: {accounts}")
        
        # Check Amount (NEW)
        amounts = intel.get("amounts", [])
        has_amount = "50000" in str(amounts)
        log_test("Amount extracted (NEW)", has_amount, f"Found: {amounts}")
        
        # Check Bank Name (NEW)
        banks = intel.get("bankNames", [])
        has_bank = "HDFC" in str(banks)
        log_test("Bank name extracted (NEW)", has_bank, f"Found: {banks}")
        
        # Check IFSC (NEW)
        ifsc = intel.get("ifscCodes", [])
        has_ifsc = "HDFC0001234" in str(ifsc)
        log_test("IFSC code extracted (NEW)", has_ifsc, f"Found: {ifsc}")
        
        # Check NO collision (phone vs account)
        phone_not_in_accounts = "9876543210" not in str(accounts)
        account_not_in_phones = "123456789012" not in str(phones)
        log_test("No phone/account collision", phone_not_in_accounts and account_not_in_phones, 
                "AI correctly disambiguated")

def test_04_response_quality():
    print(f"\n{CYAN}🎭 TEST 4: RESPONSE QUALITY & VARIATION{RESET}")
    print("-" * 50)
    
    # Send multiple messages to check variation
    messages = [
        "Why are you not replying?",
        "Send money fast!",
        "Do it immediately!",
        "Hurry up!"
    ]
    
    responses = []
    for msg in messages:
        res = send_message(msg)
        if res and res.get("reply"):
            responses.append(res.get("reply"))
    
    if len(responses) >= 3:
        # Check length variation
        lengths = [len(r.split()) for r in responses]
        length_varies = max(lengths) - min(lengths) > 3
        log_test("Response length varies", length_varies, f"Lengths: {lengths}")
        
        # Check for typos/casual language
        all_text = " ".join(responses).lower()
        casual_words = ["wat", "ok", "umm", "yeah", "im", "dont", "cant"]
        has_casual = any(word in all_text for word in casual_words)
        log_test("Contains casual language", has_casual, f"Found casual words")
        
        # Check no exact repetition
        unique_responses = len(set(responses))
        no_repetition = unique_responses == len(responses)
        log_test("No exact repetitions", no_repetition, f"{unique_responses}/{len(responses)} unique")

def test_05_interactive_conversation_simulation():
    """
    ⭐ INTERACTIVE TEST: User can enter scammer messages in real-time
    """
    print(f"\n{CYAN}💬 TEST 5: INTERACTIVE CONVERSATION SIMULATION{RESET}")
    print("-" * 50)
    
    global SESSION_ID, HISTORY
    SESSION_ID = f"interactive-{int(datetime.now().timestamp())}"
    HISTORY = []
    
    print(f"\n  {YELLOW}🎮 INTERACTIVE MODE - You are the scammer!{RESET}\n")
    print(f"  Instructions:")
    print(f"  - Type scammer messages to test the honeypot")
    print(f"  - Agent will respond naturally (5-15 words)")
    print(f"  - Type 'quit' or 'exit' to end")
    print(f"  - Type 'stats' to see extracted intelligence")
    print(f"  - Conversation ends automatically after 20 turns or when complete\n")
    
    extraction_found = {
        "upi": False,
        "phone": False,
        "bank": False,
        "amount": False,
        "ifsc": False,
        "link": False,
        "bank_name": False
    }
    
    response_quality = {
        "has_typos": False,
        "varies_length": False,
        "shows_emotion": False,
        "no_exact_repeats": True
    }
    
    prev_replies = []
    turn = 0
    max_turns = 20
    
    while turn < max_turns:
        turn += 1
        
        # Get user input
        print(f"\n  {CYAN}Turn {turn}/{max_turns}{RESET}")
        user_input = input(f"  {RED}Scammer → {RESET}").strip()
        
        # Check for commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print(f"\n  {YELLOW}Exiting interactive mode...{RESET}")
            break
        
        if user_input.lower() == 'stats':
            print(f"\n  {CYAN}📊 Current Intelligence Extracted:{RESET}")
            temp_res = send_message("continue")
            if temp_res:
                intel = temp_res.get("extractedIntelligence", {})
                for key, value in intel.items():
                    if value:
                        print(f"    {key}: {value}")
            continue
        
        if not user_input:
            print(f"  {YELLOW}(Empty message - try again){RESET}")
            turn -= 1
            continue
        
        # Send message
        print(f"  {YELLOW}Processing...{RESET}")
        res = send_message(user_input, metadata={"language": "en"})
        
        if res:
            reply = res.get("reply", "")
            intel = res.get("extractedIntelligence", {})
            scam_detected = res.get("scamDetected", False)
            
            # Display agent response
            if reply:
                word_count = len(reply.split())
                print(f"  {GREEN}Agent ({word_count} words) → {reply}{RESET}")
            else:
                print(f"  {YELLOW}Agent → (No reply - scam not detected or ignored){RESET}")
            
            # Display extracted intelligence in real-time
            print(f"\n  {CYAN}📦 Extracted This Turn:{RESET}")
            extracted_this_turn = False
            
            if intel.get("upiIds"):
                print(f"    💳 UPI: {intel['upiIds']}")
                extraction_found["upi"] = True
                extracted_this_turn = True
            if intel.get("phoneNumbers"):
                print(f"    📞 Phone: {intel['phoneNumbers']}")
                extraction_found["phone"] = True
                extracted_this_turn = True
            if intel.get("bankAccounts"):
                print(f"    🏦 Bank Account: {intel['bankAccounts']}")
                extraction_found["bank"] = True
                extracted_this_turn = True
            if intel.get("amounts"):
                print(f"    💰 Amount: ₹{', ₹'.join(intel['amounts'])}")
                extraction_found["amount"] = True
                extracted_this_turn = True
            if intel.get("bankNames"):
                print(f"    🏛️  Bank Name: {intel['bankNames']}")
                extraction_found["bank_name"] = True
                extracted_this_turn = True
            if intel.get("ifscCodes"):
                print(f"    🔢 IFSC: {intel['ifscCodes']}")
                extraction_found["ifsc"] = True
                extracted_this_turn = True
            if intel.get("phishingLinks"):
                print(f"    🔗 Link: {intel['phishingLinks']}")
                extraction_found["link"] = True
                extracted_this_turn = True
            if intel.get("suspiciousKeywords"):
                print(f"    ⚠️  Keywords: {', '.join(intel['suspiciousKeywords'][:3])}...")
            
            if not extracted_this_turn:
                print(f"    {YELLOW}(Nothing extracted this turn){RESET}")
            
            # Show detection status
            if scam_detected:
                print(f"  {RED}🚨 Status: SCAM DETECTED & ENGAGING{RESET}")
            else:
                print(f"  {YELLOW}⏳ Status: Monitoring...{RESET}")
            
            # Check extraction
            if intel.get("upiIds"):
                extraction_found["upi"] = True
            if intel.get("phoneNumbers"):
                extraction_found["phone"] = True
            if intel.get("bankAccounts"):
                extraction_found["bank"] = True
            if intel.get("amounts"):
                extraction_found["amount"] = True
            if intel.get("ifscCodes"):
                extraction_found["ifsc"] = True
            if intel.get("phishingLinks"):
                extraction_found["link"] = True
            if intel.get("bankNames"):
                extraction_found["bank_name"] = True
            
            # Check response quality
            if reply:
                # Check for typos
                typos = ["wat", "recieve", "definately", "wierd", "occured", "untill", "im", "dont", "cant", "u", "ur"]
                if any(typo in reply.lower() for typo in typos):
                    response_quality["has_typos"] = True
                
                # Check length variation
                if prev_replies:
                    prev_len = len(prev_replies[-1].split())
                    curr_len = word_count
                    if abs(prev_len - curr_len) > 3:
                        response_quality["varies_length"] = True
                
                # Check emotional words
                emotions = ["scared", "worried", "confused", "help", "please", "oh", "no", "wait"]
                if any(em in reply.lower() for em in emotions):
                    response_quality["shows_emotion"] = True
                
                # Check for exact repeats
                if reply in prev_replies:
                    response_quality["no_exact_repeats"] = False
                
                prev_replies.append(reply)
        else:
            print(f"  {RED}Error: No response from API{RESET}")
            break
        
        time.sleep(0.2)  # Brief pause
    
    # Show results
    print(f"\n  {CYAN}{'='*50}{RESET}")
    print(f"  {CYAN}📊 SIMULATION RESULTS ({turn} turns){RESET}")
    print(f"  {CYAN}{'='*50}{RESET}")
    
    print(f"\n  {CYAN}🔍 Extraction Results:{RESET}")
    log_test("  UPI Extracted", extraction_found["upi"])
    log_test("  Phone Extracted", extraction_found["phone"])
    log_test("  Bank Account Extracted", extraction_found["bank"])
    log_test("  Amount Extracted", extraction_found["amount"])
    log_test("  IFSC Extracted", extraction_found["ifsc"])
    log_test("  Link Extracted", extraction_found["link"])
    log_test("  Bank Name Extracted", extraction_found["bank_name"])
    
    print(f"\n  {CYAN}🎭 Response Quality:{RESET}")
    log_test("  Has Typos/Casual Language", response_quality["has_typos"])
    log_test("  Length Variation", response_quality["varies_length"])
    log_test("  Shows Emotion", response_quality["shows_emotion"])
    log_test("  No Exact Repeats", response_quality["no_exact_repeats"])
    
    # Overall scores
    extraction_score = sum(extraction_found.values()) / len(extraction_found) * 100
    quality_score = sum(response_quality.values()) / len(response_quality) * 100
    
    print(f"\n  {CYAN}📈 Overall Scores:{RESET}")
    print(f"       Extraction: {extraction_score:.0f}%")
    print(f"       Quality: {quality_score:.0f}%")
    print(f"\n  {GREEN}✅ Interactive simulation complete!{RESET}\n")

def test_06_guvi_schema():
    print(f"\n{CYAN}📡 TEST 6: GUVI SCHEMA COMPLIANCE{RESET}")
    print("-" * 50)
    
    res = send_message("Ok I will try now.", metadata={"language": "en"})
    
    if res:
        required_fields = ["status", "scamDetected", "engagementMetrics", "extractedIntelligence", "agentNotes"]
        all_present = all(k in res for k in required_fields)
        log_test("Required fields present", all_present, f"Fields: {list(res.keys())}")
        
        # Check extractedIntelligence structure (with NEW fields)
        intel = res.get("extractedIntelligence", {})
        expected_intel_fields = ["upiIds", "phoneNumbers", "bankAccounts", "amounts", "bankNames", "ifscCodes", "phishingLinks"]
        intel_complete = all(k in intel for k in expected_intel_fields)
        log_test("Intelligence fields complete (with NEW fields)", intel_complete, 
                f"Has: {list(intel.keys())}")
        
        # Check metrics
        metrics = res.get("engagementMetrics", {})
        has_metrics = metrics.get("totalMessagesExchanged", 0) > 0
        log_test("Engagement metrics tracked", has_metrics, f"Messages: {metrics.get('totalMessagesExchanged')}")

def main():
    print(f"{GREEN}=============================================={RESET}")
    print(f"{GREEN}   AGENTIC HONEY-POT ENHANCED TEST SUITE    {RESET}")
    print(f"{GREEN}=============================================={RESET}")
    
    try:
        test_01_language_detection()
        test_02_scam_detection()
        test_03_ai_intelligence_extraction()
        test_04_response_quality()
        test_05_interactive_conversation_simulation()  # NEW: Interactive mode
        test_06_guvi_schema()
    except Exception as e:
        print(f"\n{RED}❌ CRITICAL TEST FAILURE:{RESET} {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{GREEN}=============================================={RESET}")
    print(f"{GREEN}   TEST SUITE COMPLETE   {RESET}")
    print(f"{GREEN}=============================================={RESET}\n")
    
    print(f"{CYAN}Next Steps:{RESET}")
    print(f"  1. Review any failed tests above")
    print(f"  2. Check extraction quality (should be >80%)")
    print(f"  3. Verify responses are casual and varied")
    print(f"  4. If all pass, system is ready for deployment! 🚀")

if __name__ == "__main__":
    main()