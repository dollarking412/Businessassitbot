import os
import requests
import google.generativeai as genai
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")
        if user_text:
            reply = model.generate_content(f"Be a helpful business assistant. Reply short. User: {user_text}").text
            send_message(chat_id, reply)
    return "ok", 200

@app.route('/')
def home():
    return "Bot is running"

if __name__ == "__main__":
    # Set webhook
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook", json={"url": WEBHOOK_URL})
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
