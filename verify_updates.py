"""
Quick Verification Test for Formal Tone & Email Extraction
Tests the new formal persona and email extraction capabilities
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from datetime import datetime
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
SESSION_ID = f"verify-formal-{int(datetime.now().timestamp())}"
HISTORY = []

def send_message(text):
    """Send message and print response"""
    payload = {
        "sessionId": SESSION_ID,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": HISTORY,
        "metadata": {"language": "en"}
    }
    
    headers = {"x-api-key": "agentic_honey_pot_2026"}
    response = client.post("/api/message", json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        HISTORY.append({"role": "user", "content": text})
        if data.get("reply"):
            HISTORY.append({"role": "assistant", "content": data["reply"]})
        return data
    else:
        print(f"ERROR: {response.status_code} - {response.text}")
        return None

def main():
    print("\n" + "="*60)
    print("FORMAL TONE & EMAIL VERIFICATION")
    print("="*60 + "\n")
    
    # Test 1: Formal Tone (Lottery Scam)
    print("[TEST 1] Formal Response Check")
    print("-" * 40)
    res = send_message("Congratulations! You have won 50 Lakhs in KBC Lottery. This is manager Rajesh.")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        print("Check if response uses proper grammar (e.g. 'I am', 'Thank you', no 'omg'/'u')")
    
    print("\n")
    
    # Test 2: Email Extraction
    print("[TEST 2] Email Extraction")
    print("-" * 40)
    res = send_message("Send your details to claims@kbc-official.com immediately to process the win.")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        intel = res.get('extractedIntelligence', {})
        emails = intel.get('emailIds', [])
        print(f"Emails Extracted: {emails}")
        
        if "claims@kbc-official.com" in emails:
            print("✅ SUCCESS: Email extracted correctly")
        else:
            print("❌ FAILURE: Email not extracted")

    print("\n")
    
    # Test 3: Job Fraud (Formal Context)
    global SESSION_ID, HISTORY
    SESSION_ID = f"verify-job-{int(datetime.now().timestamp())}"
    HISTORY = []
    
    print("[TEST 3] Job Fraud Formal Tone")
    print("-" * 40)
    res = send_message("We are offering part time job. Rs 5000 daily income. Send resume to hr@jobs-online.in")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        intel = res.get('extractedIntelligence', {})
        print(f"Full Intel Object: {intel}")
        print(f"Emails Extracted: {intel.get('emailIds', [])}")
        print("Check if response is professional/polite")

if __name__ == "__main__":
    main()
