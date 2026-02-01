"""
HONEYPOT INTERACTIVE SIMULATION TOOL
------------------------------------
This script acts as the "Scammer" client, allowing you to interact directly 
with the Agentic Honey-Pot API via terminal.

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
    print("   AGENTIC HONEY-POT | INTERACTIVE SCAMMER CLI   ")
    print("="*80 + f"{RESET}")
    print("Type your message and press ENTER to send.")
    print("Type 'exit' or 'quit' to end the session.\n")

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
    session_id = f"manual-{int(time.time())}"
    history = []
    
    print(f"Target Session ID: {YELLOW}{session_id}{RESET}\n")
    
    turn_count = 0
    
    while True:
        try:
            msg = input(f"{RED}[SCAMMER]:{RESET} ").strip()
            
            if not msg:
                continue
                
            if msg.lower() in ["exit", "quit"]:
                print(f"\n{YELLOW}Terminating session...{RESET}")
                break
                
            turn_count += 1
            
            # Send to API
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
            if intel.get("upiIds") or intel.get("phoneNumbers") or intel.get("bankAccounts"):
                 print(f"   {YELLOW}Intel Extracted:{RESET} UPI={intel.get('upiIds')} Phone={intel.get('phoneNumbers')} Bank={intel.get('bankAccounts')}")

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
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    print_banner()
    run_simulation()
