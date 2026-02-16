"""
Self-Test Script for GUVI Evaluation
Tests your honeypot against GUVI's official specifications
Run: python scripts/guvi_self_test.py

Tests all 3 official GUVI scenarios:
1. Bank Fraud Detection
2. UPI Fraud Multi-turn
3. Phishing Link Detection
"""
import sys
import os
import requests
import json
import time
from datetime import datetime

# Add parent directory to path to allow imports from root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.guvi_scenarios import OFFICIAL_GUVI_SCENARIOS

# Configuration
ENDPOINT_URL = "http://127.0.0.1:7860/api/message"
API_KEY = "agentic_honey_pot_2026"


def test_api_compliance():
    """Test compliance with GUVI spec for all official scenarios"""
    
    print("\n" + "="*70)
    print("GUVI HONEYPOT API - OFFICIAL SCENARIO TESTING")
    print("="*70)
    print(f"Testing {len(OFFICIAL_GUVI_SCENARIOS)} Official Scenarios")
    
    overall_scores = []
    
    # Test each official scenario
    for scenario_index, TEST_SCENARIO in enumerate(OFFICIAL_GUVI_SCENARIOS, 1):
        print(f"\n{'='*70}")
        print(f"SCENARIO {scenario_index}/{len(OFFICIAL_GUVI_SCENARIOS)}: {TEST_SCENARIO['name']}")
        print(f"{'='*70}")
        
        session_id = f"test-{TEST_SCENARIO['scenarioId']}-{int(time.time())}"
        conversation_history = []
        
        print(f"Scenario: {TEST_SCENARIO['description']}")
        print(f"Type: {TEST_SCENARIO['scamType']}")
        print(f"Channel: {TEST_SCENARIO['metadata']['channel']}")
        print(f"Session ID: {session_id}\n")
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
        
        # Store responses for final evaluation
        all_responses = []
        start_time = time.time()
        
        # Simulate conversation turns (using 3 turns for testing)
        MAX_TEST_TURNS = min(3, TEST_SCENARIO.get('maxTurns', 10))
        
        for turn in range(1, MAX_TEST_TURNS + 1):
            print(f"{'='*70}")
            print(f"TURN {turn}/{MAX_TEST_TURNS}")
            print(f"{'='*70}")
            
            # Generate scammer message
            if turn == 1:
                scammer_message = TEST_SCENARIO['initialMessage']
            else:
                # Simple follow-up templates based on scenario type
                if TEST_SCENARIO['scamType'] == 'bank_fraud':
                    follow_ups = [
                        "Just share the first 4 digits and I can verify",
                        "My system is showing your account needs immediate verification"
                    ]
                elif TEST_SCENARIO['scamType'] == 'upi_fraud':
                    follow_ups = [
                        "Please share your UPI ID for verification",
                        "We need your phone number registered with UPI"
                    ]
                else:  # phishing
                    follow_ups = [
                        "Click the link to claim your prize now",
                        "Limited time offer! Complete verification at our portal"
                    ]
                
                scammer_message = follow_ups[turn - 2] if turn - 2 < len(follow_ups) else "Still waiting for your details"
            
            print(f"Scammer: {scammer_message[:80]}...\n")
            
            # Prepare request
            message = {
                "sender": "scammer",
                "text": scammer_message,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            request_body = {
                'sessionId': session_id,
                'message': message,
                'conversationHistory': conversation_history,
                'metadata': TEST_SCENARIO['metadata']
            }
            
            # Test 1: Response Time
            turn_start = time.time()
            try:
                response = requests.post(
                    ENDPOINT_URL,
                    headers=headers,
                    json=request_body,
                    timeout=35  # GUVI max is 30s
                )
                turn_end = time.time()
                response_time = turn_end - turn_start
                
                print(f"[OK] Response Time: {response_time:.2f}s (Limit: 30s)")
                
                if response_time > 30:
                    print(f"[WARN] WARNING: Response exceeded 30s limit!")
                
                # Test 2: HTTP Status 200
                if response.status_code != 200:
                    print(f"[FAIL] FAIL - Status: {response.status_code} (Expected: 200)")
                    print(f"   Response: {response.text}")
                    break
                print(f"[OK] HTTP Status: 200")
                
                response_data = response.json()
                all_responses.append(response_data)
                
                # Test 3: Required Fields
                print(f"\n[INFO] Response Fields:")
                
                # status field
                has_status = 'status' in response_data
                status = '[OK]' if has_status else '[FAIL]'
                print(f"   {status} status: {response_data.get('status', 'MISSING')}")
                
                # scamDetected field
                has_scam = 'scamDetected' in response_data
                scam_status = '[OK]' if has_scam else '[FAIL]'
                print(f"   {scam_status} scamDetected: {response_data.get('scamDetected', 'MISSING')}")
                
                # extractedIntelligence field
                if 'extractedIntelligence' in response_data:
                    intel = response_data['extractedIntelligence']
                    print(f"   [OK] extractedIntelligence:")
                    if intel.get('phoneNumbers'):
                        print(f"      [+] Phones: {intel['phoneNumbers']}")
                    if intel.get('bankAccounts'):
                        print(f"      [+] Accounts: {intel['bankAccounts']}")
                    if intel.get('upiIds'):
                        print(f"      [+] UPIs: {intel['upiIds']}")
                    if intel.get('phishingLinks'):
                        print(f"      [+] Links: {intel['phishingLinks']}")
                else:
                    print(f"   [FAIL] extractedIntelligence: MISSING")
                
                # reply field
                reply = response_data.get('reply') or response_data.get('message') or response_data.get('text')
                if reply:
                    print(f"   [OK] reply: '{reply[:50]}...'")
                else:
                    print(f"   [FAIL] reply: MISSING")
                
                # Update conversation history
                conversation_history.append(message)
                conversation_history.append({
                    'sender': 'user',
                    'text': reply or 'No response',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                })
                
            except requests.exceptions.Timeout:
                print(f"[FAIL] FAIL - Request Timeout (>30s)")
                break
            except requests.exceptions.ConnectionError as e:
                print(f"[FAIL] FAIL - Connection Error: {e}")
                break
            except Exception as e:
                print(f"[FAIL] FAIL - Exception: {e}")
                break
        
        # Evaluate this scenario
        total_time = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"Scenario Results:")
        print(f"{'='*70}")
        print(f"Turns Completed: {MAX_TEST_TURNS}")
        print(f"Messages Exchanged: {len(conversation_history)}")
        print(f"Total Time: {total_time:.2f}s")
        
        # Score Calculation
        scores = evaluate_responses(all_responses, TEST_SCENARIO, conversation_history)
        print(f"\n[SCORE] Scenario Score Breakdown:")
        print(f"   Scam Detection: {scores['scam_detection']}/20")
        print(f"   Intelligence Extraction: {scores['intelligence_extraction']}/40")
        print(f"   Engagement Quality: {scores['engagement_quality']}/20")
        print(f"   Response Structure: {scores['response_structure']}/20")
        print(f"   SCENARIO TOTAL: {scores['total']}/100")
        
        overall_scores.append({
            'scenario': TEST_SCENARIO['name'],
            'score': scores['total'],
            'weight': TEST_SCENARIO.get('weight', 1)
        })
    
    # Final Overall Report
    print(f"\n{'='*70}")
    print("FINAL OVERALL REPORT")
    print(f"{'='*70}")
    
    total_weighted_score = 0
    total_weight = 0
    
    for result in overall_scores:
        weight = result['weight']
        score = result['score']
        weighted = (score / 100.0) * weight
        total_weighted_score += weighted
        total_weight += weight
        
        print(f"\n{result['scenario']}: {score}/100 (weight: {weight})")
        print(f"   Contribution: {weighted:.1f} points")
    
    final_score = (total_weighted_score / total_weight * 100) if total_weight > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"[SCORE] WEIGHTED FINAL SCORE: {final_score:.1f}/100")
    print(f"{'='*70}")
    
    print(f"\n[OK] EVALUATION COMPLETE - All {len(OFFICIAL_GUVI_SCENARIOS)} scenarios tested")
    print("="*70 + "\n")


def evaluate_responses(responses, scenario, conversation_history):
    """Evaluate responses using GUVI scoring logic"""
    
    scores = {
        'scam_detection': 0,
        'intelligence_extraction': 0,
        'engagement_quality': 0,
        'response_structure': 0,
        'total': 0
    }
    
    if not responses:
        return scores
    
    # Use last response for scam detection
    last_response = responses[-1]
    
    # 1. Scam Detection (20 points)
    if last_response.get('scamDetected', False):
        scores['scam_detection'] = 20
    
    # 2. Intelligence Extraction (40 points)
    extracted = last_response.get('extractedIntelligence', {})
    fake_data = scenario.get('fakeData', {})
    
    intel_map = {
        'bankAccount': 'bankAccounts',
        'upiId': 'upiIds',
        'phoneNumber': 'phoneNumbers'
    }
    
    for fake_key, fake_value in fake_data.items():
        output_key = intel_map.get(fake_key, fake_key)
        extracted_list = extracted.get(output_key, [])
        
        if isinstance(extracted_list, list):
            if any(fake_value in str(v) for v in extracted_list):
                scores['intelligence_extraction'] += 10
    
    scores['intelligence_extraction'] = min(scores['intelligence_extraction'], 40)
    
    # 3. Engagement Quality (20 points)
    metrics = last_response.get('engagementMetrics', {})
    duration = metrics.get('engagementDurationSeconds', 0)
    messages = metrics.get('totalMessagesExchanged', 0)
    
    if duration > 0:
        scores['engagement_quality'] += 5
    if duration > 60:
        scores['engagement_quality'] += 5
    if messages > 0:
        scores['engagement_quality'] += 5
    if messages >= 5:
        scores['engagement_quality'] += 5
    
    # 4. Response Structure (20 points)
    required = ['status', 'scamDetected', 'extractedIntelligence']
    optional = ['engagementMetrics', 'agentNotes']
    
    for field in required:
        if field in last_response:
            scores['response_structure'] += 5
    
    for field in optional:
        if field in last_response and last_response[field]:
            scores['response_structure'] += 2.5
    
    scores['response_structure'] = min(scores['response_structure'], 20)
    
    # Total
    scores['total'] = sum([
        scores['scam_detection'],
        scores['intelligence_extraction'],
        scores['engagement_quality'],
        scores['response_structure']
    ])
    
    return scores


if __name__ == "__main__":
    print("\n[*] Starting GUVI API Compliance Test...\n")
    test_api_compliance()
