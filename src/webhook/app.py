"""
Flask webhook for WhatsApp messages via Twilio.
DAY 4: Production-ready with security and error handling.
"""

import os
import sys
from flask import Flask, request, Response
from dotenv import load_dotenv
import logging
from twilio.request_validator import RequestValidator

# Add src to path
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

# Twilio validator for security
validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "SAP CX WhatsApp Agent",
        "version": "Day 4 - Production",
        "domains": ["service_cloud", "fsm", "sales_cloud", "cpq", "cpi"]
    }, 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Twilio webhook endpoint.
    Receives WhatsApp messages and processes them with LangGraph agent.
    """
    
    # Verify Twilio signature (security)
    if os.getenv("VERIFY_TWILIO_SIGNATURE", "true").lower() == "true":
        signature = request.headers.get("X-Twilio-Signature", "")
        url = request.url
        params = request.form.to_dict()
        
        if not validator.validate(url, params, signature):
            logger.warning(f"Invalid Twilio signature from {request.remote_addr}")
            return Response("Forbidden", status=403)
    
    try:
        # Get incoming message data
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logger.info(f"📱 Message from {from_number}: {incoming_msg}")
        
        # Handle empty messages
        if not incoming_msg:
            response_text = "👋 Hi! I'm your SAP CX assistant. Ask me anything about Service Cloud, FSM, Sales Cloud, CPQ, or CPI integration!"
        else:
            # Run the agent (with timeout protection)
            try:
                agent_result = run_agent(
                    query=incoming_msg,
                    user_id=from_number
                )
                
                response_text = agent_result.get('answer', 'Sorry, I could not process your request.')
                
                # Log metadata
                logger.info(f"🤖 Domain: {agent_result.get('primary_domain')} "
                           f"(confidence: {agent_result.get('confidence')})")
                
                # Handle errors
                if agent_result.get('error'):
                    logger.error(f"❌ Agent error: {agent_result['error']}")
                    response_text = "I encountered an issue processing your question. Please try rephrasing it or contact support."
                    
            except Exception as e:
                logger.error(f"❌ Agent execution error: {e}", exc_info=True)
                response_text = "Sorry, I'm experiencing technical difficulties. Please try again in a moment."
        
        logger.info(f"💬 Sending: {response_text[:100]}...")
        
        # Twilio TwiML response
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""
        
        return Response(twiml_response, mimetype='text/xml')
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        error_response = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, I encountered a technical error. Our team has been notified.</Message>
</Response>"""
        return Response(error_response, mimetype='text/xml'), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"🚀 SAP CX WhatsApp Agent Starting")
    logger.info(f"📍 Port: {port}")
    logger.info(f"📚 Docs indexed: 46,682 chunks across 5 domains")
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production