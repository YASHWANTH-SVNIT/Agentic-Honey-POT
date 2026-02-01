"""
HONEYPOT SIMULATION TOOL
------------------------
This script simulates a complete end-to-end attack scenario on the Agentic Honey-Pot.
It acts as a "Scammer" sending messages to your local API.

PREREQUISITES:
1. Ensure the API server is running: `uvicorn main:app --reload`
2. Ensure you have a valid .env file

USAGE:
python simulate_scam_attack.py
"""

import requests
import json
import time
import sys
from datetime import datetime

# CONFIGURATION
API_URL = "http://127.0.0.1:8000/api/message"
API_KEY = "agentic_honey_pot_2026"  # Matches .env key

# COLORS
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_banner():
    print(f"{BLUE}" + "="*80)
    print("   AGENTIC HONEY-POT | ATTACK SIMULATION   ")
    print("="*80 + f"{RESET}")

def send_message(session_id, message_text, history):
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text,
            "timestamp": datetime.now().isoformat()
        },
        "conversationHistory": history
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response
    except requests.exceptions.ConnectionError:
        print(f"{RED}[CRITICAL] Could not connect to API at {API_URL}{RESET}")
        print("Please ensure the server is running: uvicorn main:app --reload")
        sys.exit(1)

def run_simulation():
    session_id = f"sim-{int(time.time())}"
    history = []
    
    # SCENARIO: Digital Arrest Scam (CBI Impersonation)
    # Designed to trigger: Detection -> Engagement -> Extraction -> termination
    scammer_script = [
        "This is Officer Rajesh Kumar from CBI Delhi. We have found your Aadhaar linked to money laundering.",
        "A parcel with drugs was seized in your name. An arrest warrant is issued. Do not disconnect.",
        "You must verify your identity immediately via video call. Join this Zoom meeting ID: 555-123-999.",
        "If you do not cooperate, we will freeze your bank accounts. Tell me which bank you use.",
        "Transfer a security deposit of Rs 50,000 to verify your funds. UPI: rajesh.cbi@paytm",
        "This is a refundable amount. Do it now or police will come to your home.",
        "Why are you delaying? The warrant needs to be cancelled immediately.",
        "Send the screenshot of payment. Urgent."
    ]

    print(f"Target Session ID: {YELLOW}{session_id}{RESET}\n")
    
    start_time = time.time()
    
    for i, msg in enumerate(scammer_script, 1):
        print(f"{RED}[SCAMMER Turn {i}]:{RESET} {msg}")
        
        # Add latency simulation
        time.sleep(1) 
        
        resp = send_message(session_id, msg, history)
        
        if resp.status_code != 200:
            print(f"{RED}API Error {resp.status_code}: {resp.text}{RESET}")
            break
            
        data = resp.json()
        
        # DISPLAY RESPONSE
        scam_status = f"{RED}DETECTED{RESET}" if data.get("scamDetected") else f"{GREEN}CLEAN{RESET}"
        print(f"{BLUE}[HONEYPOT]:{RESET} {data.get('reply')}")
        print(f"   Status: {scam_status} | Action: {data.get('action')}")
        
        # Show extraction progress
        intel = data.get("extractedIntelligence", {})
        if intel.get("upiIds") or intel.get("phoneNumbers"):
             print(f"   {YELLOW}Intel Extracted:{RESET} UPI={intel.get('upiIds')} Phone={intel.get('phoneNumbers')}")

        print("-" * 50)
        
        # Update History
        history.append({"sender": "scammer", "text": msg})
        if data.get("reply"):
            history.append({"sender": "agent", "text": data["reply"]})
            
        # Check for Session End
        if data.get("action") == "session_ended":
            print(f"\n{GREEN}>>> SIMULATION ENDED BY AGENT (STOP CONDITION MET) <<<{RESET}")
            print(f"Agent Notes: {data.get('agentNotes')}")
            break

    total_time = time.time() - start_time
    print(f"\n{BLUE}Simulation Complete in {total_time:.2f}s{RESET}")

if __name__ == "__main__":
    print_banner()
    run_simulation()
