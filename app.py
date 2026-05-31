import os
import requests
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

# Get tokens from environment
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini AI
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    AI_AVAILABLE = True
else:
    AI_AVAILABLE = False
    print("WARNING: GEMINI_API_KEY not set, using fallback replies")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Error sending: {e}")

def get_ai_reply(user_message):
    if AI_AVAILABLE:
        try:
            response = model.generate_content(
                f"You are BizAssist AI, a professional customer support chatbot for businesses. "
                f"Keep replies helpful, friendly, and under 2 sentences. "
                f"User asked: {user_message}"
            )
            return response.text.strip()
        except Exception as e:
            print(f"AI Error: {e}")
            return f"Sorry, I'm having technical issues. Please try again."
    else:
        # Fallback responses when no Gemini key
        msg = user_message.lower()
        if "hello" in msg or "hi" in msg:
            return "Hello! How can I help your business today?"
        elif "hour" in msg or "open" in msg:
            return "Our business hours are 9 AM to 6 PM, Monday through Friday."
        elif "price" in msg or "cost" in msg:
            return "Please visit our website or contact sales for pricing details."
        else:
            return f"Thanks for your message! A representative will get back to you soon."

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        if update and 'message' in update:
            chat_id = update['message']['chat']['id']
            text = update['message'].get('text', '')
            
            if text:
                # Get AI reply or fallback
                reply = get_ai_reply(text)
                send_message(chat_id, reply)
        
        return 'ok', 200
    except Exception as e:
        print(f"Error: {e}")
        return 'ok', 200

@app.route('/')
def home():
    return "BizAssist AI is running with Gemini!"

if __name__ == '__main__':
    # Set webhook on startup
    webhook_url = f"https://businessassitbot-yhj7.onrender.com/{TOKEN}"
    set_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.post(set_url)
    print(f"Webhook set: {response.json()}")
    
    # Print AI status
    if AI_AVAILABLE:
        print("✅ Gemini AI is ENABLED - Bot will give smart replies")
    else:
        print("⚠️ Gemini AI is DISABLED - Add GEMINI_API_KEY for smart replies")
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
