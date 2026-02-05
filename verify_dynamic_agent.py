"""
Quick Verification Test for Dynamic Agent System
Tests the new adaptive components
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from datetime import datetime
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
SESSION_ID = f"verify-{int(datetime.now().timestamp())}"
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
    print("DYNAMIC AGENT SYSTEM VERIFICATION")
    print("="*60 + "\n")
    
    # Test 1: Digital Arrest Scam (should be scared)
    print("[TEST 1] Digital Arrest Scam")
    print("-" * 40)
    res = send_message("This is CBI police. Your Aadhaar is linked to money laundering. You are under digital arrest!")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        print(f"Scam Detected: {res.get('scamDetected')}")
        print(f"Intel: {list(res.get('extractedIntelligence', {}).keys())}")
    
    print("\n")
    
    # Test 2: Follow up with payment request
    print("[TEST 2] Payment Request")
    print("-" * 40)
    res = send_message("Pay Rs 50000 to UPI: police.verify@sbi immediately or we will arrest you!")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        intel = res.get('extractedIntelligence', {})
        print(f"UPI Extracted: {intel.get('upiIds', [])}")
        print(f"Amount Extracted: {intel.get('amounts', [])}")
    
    print("\n")
    
    # Test 3: New session - Lottery Scam (should be excited)
    global SESSION_ID, HISTORY
    SESSION_ID = f"verify-lottery-{int(datetime.now().timestamp())}"
    HISTORY = []
    
    print("[TEST 3] Lottery Scam (Different Emotion)")
    print("-" * 40)
    res = send_message("Congratulations! You have won Rs 10 lakh in KBC lottery! Claim your prize now!")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        print(f"Scam Detected: {res.get('scamDetected')}")
    
    print("\n")
    
    # Test 4: Lottery follow up
    print("[TEST 4] Lottery Payment Request")
    print("-" * 40)
    res = send_message("To claim prize, pay Rs 5000 processing fee to 9876543210 via PhonePe")
    if res:
        print(f"Reply: {res.get('reply', 'NO REPLY')}")
        intel = res.get('extractedIntelligence', {})
        print(f"Phone Extracted: {intel.get('phoneNumbers', [])}")
        print(f"Amount Extracted: {intel.get('amounts', [])}")
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    
    print("\nCheck if:")
    print("  - Digital arrest responses sound SCARED")
    print("  - Lottery responses sound EXCITED")
    print("  - Intelligence is being extracted")
    print("  - Responses are natural length (not just 5 words)")

if __name__ == "__main__":
    main()
