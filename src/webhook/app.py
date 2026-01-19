"""
Flask webhook for WhatsApp messages via Twilio.
Day 1: Basic webhook that logs messages and sends mock responses.
"""

import os
from flask import Flask, request, Response
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "SAP CX WhatsApp Agent"}, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Twilio webhook endpoint.
    Receives WhatsApp messages and processes them.
    """
    try:
        # Get incoming message data
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logger.info(f"📱 Received message from {from_number}: {incoming_msg}")
        
        # For Day 1: Simple mock response
        # Days 2-4: This will call the actual agent
        response_text = mock_agent_response(incoming_msg)
        
        logger.info(f"🤖 Sending response: {response_text}")
        
        # Twilio expects TwiML response
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""
        
        return Response(twiml_response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, I encountered an error. Please try again.</Message>
</Response>"""
        return Response(error_response, mimetype='text/xml'), 500

def mock_agent_response(message: str) -> str:
    """
    Mock agent for Day 1 testing.
    Replace with real agent on Day 2.
    """
    message_lower = message.lower()
    
    # Simple keyword matching for testing
    if "service cloud" in message_lower or "ticket" in message_lower:
        return "🎯 I detected a Service Cloud question! (This is a test response - real agent coming on Day 2)"
    elif "fsm" in message_lower or "field service" in message_lower:
        return "🎯 I detected an FSM question! (This is a test response - real agent coming on Day 2)"
    elif "cpi" in message_lower or "integration" in message_lower:
        return "🎯 I detected a CPI question! (This is a test response - real agent coming on Day 2)"
    else:
        return f"👋 Hi! I'm your SAP CX assistant. You asked: '{message}' (Test mode - Day 1)"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)