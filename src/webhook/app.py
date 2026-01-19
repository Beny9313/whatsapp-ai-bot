"""
Flask webhook for WhatsApp messages via Twilio.
Day 2: Integrated with LangGraph agent for real SAP CX responses.
"""

import os
import sys
from flask import Flask, request, Response
from dotenv import load_dotenv
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.agents.sap_agent import run_agent

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
    return {"status": "ok", "service": "SAP CX WhatsApp Agent", "version": "Day 2 - LangGraph"}, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Twilio webhook endpoint.
    Receives WhatsApp messages and processes them with LangGraph agent.
    """
    try:
        # Get incoming message data
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logger.info(f"📱 Received from {from_number}: {incoming_msg}")
        
        # Run the LangGraph agent (Day 2 - REAL AGENT!)
        agent_result = run_agent(
            query=incoming_msg,
            user_id=from_number  # Use WhatsApp number as user ID
        )
        
        # Extract answer
        response_text = agent_result.get('answer', 'Sorry, I could not process your request.')
        
        # Log agent metadata
        logger.info(f"🤖 Agent classified as: {agent_result.get('primary_domain')} "
                   f"(confidence: {agent_result.get('confidence')})")
        logger.info(f"💬 Sending response ({len(response_text)} chars)")
        
        # Handle errors
        if agent_result.get('error'):
            logger.error(f"❌ Agent error: {agent_result['error']}")
            response_text = "Sorry, I encountered an error. Please try rephrasing your question."
        
        # Twilio expects TwiML response
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""
        
        return Response(twiml_response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, I encountered a technical error. Please try again later.</Message>
</Response>"""
        return Response(error_response, mimetype='text/xml'), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"🚀 Starting SAP CX Agent (Day 2 - LangGraph)")
    logger.info(f"📍 Listening on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)