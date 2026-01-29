"""
Test script for Phase 3 Engagement Pipeline
Simulates a multi-turn conversation with a scammer
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
    session_id = "dev-test-conversation-01"
    history = []
    
    # Simulated scammer messages
    scammer_messages = [
        "This is Officer Sharma from CBI. Your Aadhaar is linked to money laundering case.",
        "You must join video call immediately or arrest warrant will be issued. Call 9876543210",
        "Pay security deposit of Rs 50,000 to paytm@cbi.gov for verification",
        "Send OTP received on your phone to verify identity",
        "Final warning! Transfer to UPI: scammer123@paytm now!"
    ]
    
    print("=" * 80)
    print("PHASE 3 ENGAGEMENT PIPELINE TEST")
    print("=" * 80)
    print()
    
    for i, scammer_msg in enumerate(scammer_messages, 1):
        print(f"\n{'='*80}")
        print(f"TURN {i}")
        print(f"{'='*80}")
        print(f"\n[SCAMMER]: {scammer_msg}")
        
        # Send message
        response = send_message(session_id, scammer_msg, history)
        
        # Display response
        print(f"\n[AGENT ({response['metadata']['persona']})]: {response['reply']}")
        print(f"\nMetadata:")
        print(f"  - Stage: {response['metadata']['stage']}")
        print(f"  - Turn: {response['metadata']['turn']}")
        print(f"  - Category: {response['metadata']['category']}")
        print(f"  - Extracted Intel: {json.dumps(response['metadata']['extracted_intel'], indent=4)}")
        
        # Update history
        history.append({"sender": "scammer", "text": scammer_msg})
        history.append({"sender": "agent", "text": response['reply']})
        
        # Stop if session ended
        if response['action'] == 'session_ended':
            print("\n[SESSION ENDED]")
            break
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
