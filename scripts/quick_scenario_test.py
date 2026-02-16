"""
Quick test of one scenario to verify API connectivity
"""
import sys
import os
import requests
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.guvi_scenarios import OFFICIAL_GUVI_SCENARIOS

ENDPOINT_URL = "http://127.0.0.1:7860/api/message"
API_KEY = "agentic_honey_pot_2026"

# Test just the first scenario with 1 turn
scenario = OFFICIAL_GUVI_SCENARIOS[0]
print(f"\n[*] Testing Scenario: {scenario['name']}")
print(f"[*] Endpoint: {ENDPOINT_URL}")

session_id = f"quick-test-{int(datetime.now().timestamp())}"

message = {
    "sender": "scammer",
    "text": scenario['initialMessage'],
    "timestamp": datetime.utcnow().isoformat() + "Z"
}

request_body = {
    'sessionId': session_id,
    'message': message,
    'conversationHistory': [],
    'metadata': scenario['metadata']
}

headers = {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY
}

print(f"\n[*] Sending request to API...")
print(f"    Message: {scenario['initialMessage'][:50]}...")

try:
    import time
    start = time.time()
    response = requests.post(
        ENDPOINT_URL,
        headers=headers,
        json=request_body,
        timeout=35
    )
    elapsed = time.time() - start
    
    print(f"\n[OK] Response received in {elapsed:.2f}s")
    print(f"[OK] Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Response fields:")
        print(f"    - status: {data.get('status')}")
        print(f"    - scamDetected: {data.get('scamDetected')}")
        if 'extractedIntelligence' in data:
            intel = data['extractedIntelligence']
            print(f"    - extractedIntelligence:")
            for key, val in intel.items():
                if val:
                    print(f"        {key}: {val}")
        if 'reply' in data:
            print(f"    - reply: {data['reply'][:60]}...")
        print(f"\n[OK] API is working correctly!")
    else:
        print(f"[FAIL] Status code {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
