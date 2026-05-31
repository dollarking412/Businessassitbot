import os
import logging
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify

# Setup logging to see everything in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Get environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Make sure this is correct in Render

# Check for missing variables at startup
if not TELEGRAM_TOKEN:
    logger.error("FATAL: TELEGRAM_BOT_TOKEN environment variable not set!")
if not GEMINI_API_KEY:
    logger.error("FATAL: GEMINI_API_KEY environment variable not set!")
if not WEBHOOK_URL:
    logger.error("FATAL: WEBHOOK_URL environment variable not set!")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def send_message(chat_id, text):
    """Safely send a message back to the user."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        logger.info(f"Message sent successfully to chat_id: {chat_id}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Main entry point for Telegram updates."""
    try:
        # Get the update from Telegram
        update = request.get_json()
        if not update:
            logger.warning("Received empty update.")
            return "ok", 200

        logger.info(f"Received update: {update}")

        # Process the message if it exists
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            user_text = update["message"].get("text", "")

            if not user_text:
                logger.info(f"Received non-text message from {chat_id}")
                send_message(chat_id, "Sorry, I can only process text messages for now.")
                return "ok", 200

            logger.info(f"Processing message from {chat_id}: '{user_text}'")

            # Get AI reply
            try:
                response = model.generate_content(
                    f"You are BizAssist AI, a professional customer support chatbot for businesses. "
                    f"Keep replies short, under 3 sentences. User: {user_text}"
                )
                reply = response.text.strip()
                logger.info(f"AI generated reply: '{reply}'")
            except Exception as ai_error:
                logger.error(f"Gemini API error: {ai_error}")
                reply = "Sorry, I'm having trouble thinking right now. Please try again in a moment."

            # Send the reply
            send_message(chat_id, reply)

    except Exception as e:
        logger.error(f"Unhandled exception in webhook: {e}", exc_info=True)

    # Always return 200 OK to Telegram
    return "ok", 200

@app.route('/', methods=['GET'])
def home():
    """Simple health check endpoint."""
    return "BizAssist AI is running and healthy!", 200

@app.route('/setwebhook', methods=['GET'])
def set_webhook_route():
    """A manual route to set the webhook."""
    if not TELEGRAM_TOKEN or not WEBHOOK_URL:
        return jsonify({"error": "Missing TELEGRAM_TOKEN or WEBHOOK_URL"}), 500

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}"
    try:
        response = requests.post(url, timeout=10)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # This block only runs locally, not on Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
