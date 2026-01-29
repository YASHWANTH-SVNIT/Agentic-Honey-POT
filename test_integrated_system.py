"""
Test script for integrated Phase 2 + Phase 3 system
Tests detection followed by engagement
"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/message"
API_KEY = "agentic_honey_pot_2026"

def send_message(session_id, message_text, history):
    """Send a message to the API"""
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": message_text
        },
        "conversationHistory": history
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    return response.json()

def main():
    session_id = "test-integrated-001"
    history = []
    
    # Test messages
    messages = [
        "This is Officer Sharma from CBI. Your Aadhaar is linked to money laundering case.",
        "You must join video call immediately or arrest warrant will be issued. Call 9876543210",
        "Pay security deposit of Rs 50,000 to paytm@cbi.gov for verification"
    ]
    
    print("=" * 80)
    print("INTEGRATED PHASE 2 + PHASE 3 TEST")
    print("=" * 80)
    print()
    
    for i, msg in enumerate(messages, 1):
        print(f"\n{'='*80}")
        print(f"TURN {i}")
        print(f"{'='*80}")
        print(f"\n[SCAMMER]: {msg}")
        
        # Send message
        response = send_message(session_id, msg, history)
        
        # Display response
        print(f"\n[SYSTEM]: {response.get('reply', 'No reply')}")
        print(f"\nAction: {response['action']}")
        print(f"Metadata: {json.dumps(response.get('metadata', {}), indent=2)}")
        
        # Update history
        history.append({"sender": "scammer", "text": msg})
        if response.get('reply'):
            history.append({"sender": "agent", "text": response['reply']})
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
