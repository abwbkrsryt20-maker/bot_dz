from flask import Flask, request
import requests

app = Flask(__name__)
TOKEN = "9232668538:AAEwX6AWbxuDu5MxGtFpf5tXZMVbAp3NcSo"

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        cid = data["message"]["chat"]["id"]
        txt = data["message"]["text"]
        msg = "⚡ مرحباً بك في بوت نوتي برو! أرسل رقم هاتفك (10 أرقام):"
        if len(txt) == 10 and txt.isdigit():
            msg = f"✅ تم استلام الرقم {txt} بنجاح!"
        requests.post(f"https://telegram.org{TOKEN}/sendMessage", json={"chat_id": cid, "text": msg})
    return "OK", 200
