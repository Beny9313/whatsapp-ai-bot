"""
Test script to verify webhook works locally.
Simulates Twilio sending a WhatsApp message.
"""

import requests
import sys
import os

def test_webhook(message: str, base_url: str = None):
    """Send a test message to webhook"""
    
    # Allow override via environment variable for Codespaces
    if base_url is None:
        base_url = os.getenv("WEBHOOK_URL", "http://localhost:5000")
    
    url = f"{base_url}/webhook"
    
    # Simulate Twilio's POST request format
    payload = {
        'Body': message,
        'From': 'whatsapp:+1234567890',  # Mock sender
        'To': 'whatsapp:+0987654321'     # Mock recipient
    }
    
    print(f"\n📤 Sending test message: '{message}'")
    print(f"🎯 Target: {url}\n")
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ Webhook responded successfully!")
            print(f"\n📥 Response:\n{response.text}\n")
        else:
            print(f"❌ Webhook error! Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook!")
        print("Make sure Flask app is running: python src/webhook/app.py")
        print(f"Or set WEBHOOK_URL environment variable to your Codespaces forwarded URL")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Test cases
    test_cases = [
        "How do I configure service tickets in Service Cloud?",
        "FSM work order scheduling",
        "CPI integration setup",
        "Hello, are you there?"
    ]
    
    print("="*80)
    print("LOCAL WEBHOOK TESTING")
    print("="*80)
    
    # Get webhook URL
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        print(f"Using Codespaces URL: {webhook_url}\n")
    else:
        print("Using localhost:5000 (set WEBHOOK_URL env var for Codespaces)\n")
    
    for test_msg in test_cases:
        test_webhook(test_msg, webhook_url)
        print("-"*80)
