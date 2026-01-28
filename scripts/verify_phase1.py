import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {
    "x-api-key": "default-secret-key", # This matches the default in app/api/dependencies.py
    "Content-Type": "application/json"
}

def test_health():
    print("Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_message_routing():
    print("Testing /message endpoint (Phase 1 Routing)...")
    payload = {
        "sessionId": "test-session-123",
        "message": {
            "sender": "scammer",
            "text": "Hello, this is CBI. You are under arrest.",
            "timestamp": "2026-01-28T10:00:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS"}
    }
    
    response = requests.post(f"{BASE_URL}/message", headers=HEADERS, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    try:
        test_health()
        test_message_routing()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the server is running on http://127.0.0.1:8000")
