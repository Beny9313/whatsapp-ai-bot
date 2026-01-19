"""
Advanced webhook testing with agent verification.
Tests the full pipeline: webhook → agent → response
"""

import requests
import time

def test_agent_webhook(message: str, port: int = 5000):
    """Test webhook with detailed agent inspection"""
    
    url = f"http://localhost:{port}/webhook"
    payload = {
        'Body': message,
        'From': 'whatsapp:+1234567890',
        'To': 'whatsapp:+0987654321'
    }
    
    print(f"\n{'='*80}")
    print(f"📤 QUERY: {message}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            # Extract answer from TwiML
            answer = response.text.split("<Message>")[1].split("</Message>")[0]
            
            print(f"✅ SUCCESS ({elapsed:.2f}s)")
            print(f"\n💬 ANSWER:\n{answer}\n")
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️ TIMEOUT after 30 seconds")
        print("Agent might be too slow (we'll optimize on Day 4)")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("AGENT WEBHOOK END-TO-END TEST")
    print("="*80)
    
    # Test cases covering different domains
    test_cases = [
        "How do I configure automated ticket assignment in Service Cloud?",
        "What's the process for FSM work order scheduling?",
        "How do I set up OAuth authentication in CPI?",
        "Help me create a CPQ quote template",
        "How does Service Cloud integrate with CPI for ticket data?"  # Cross-domain
    ]
    
    for query in test_cases:
        test_agent_webhook(query)
        print("-"*80)