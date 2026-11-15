from flask import Flask, request
import requests

app = Flask(__name__)
TOKEN = "9232668538:AAEwX6AWbxuDu5MxGtFpf5tXZMVbAp3NcSo"
URL = "https://onrender.com"

@app.route('/')
def index():
    r = requests.get(f"https://telegram.org{TOKEN}/setWebhook?url={URL}/webhook")
    return r.text

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"]["text"]
        if text == "/start":
            requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "⚡ أهلاً بك في بوت نوتي برو! أرسل رقم هاتفك (10 أرقام) للبدء:"
            })
        elif len(text) == 10 and text.isdigit():
            requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"✅ تم استلام الرقم {text}! جاري فحص العروض المتاحة..."
            })
        else:
            requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "❌ يرجى إرسال رقم هاتف صحيح من 10 أرقام."
            })
    return "OK", 200
