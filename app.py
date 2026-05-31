import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# Get tokens from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Error sending: {e}")

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update and 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text:
                # Simple reply without Gemini for testing
                send_message(chat_id, f"Hello! You said: {text}")
        
        return 'ok', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'ok', 200

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == '__main__':
    # Set webhook
    webhook_url = f"https://businessassitbot-yhj7.onrender.com/{TOKEN}"
    set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.post(set_url)
    print(f"Webhook set: {response.json()}")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
