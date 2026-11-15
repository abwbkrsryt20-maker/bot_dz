from flask import Flask, request
import requests

app = Flask(__name__)

BOT_TOKEN = "9232668538:AAEwX6AWbxuDu5MxGtFpf5tXZMVbAp3NcSo"
RENDER_URL = "https://onrender.com"

user_sessions = {}

@app.route('/')
def home():
    res = requests.get(f"https://telegram.org{BOT_TOKEN}/setWebhook?url={RENDER_URL}/webhook")
    return f"البوت يعمل بنجاح! حالة الربط: {res.text}"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"].strip()
        handle_message(chat_id, text)
        
    elif "callback_query" in update:
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        data = update["callback_query"]["data"]
        handle_button(chat_id, data)
        
    return "OK", 200

def handle_message(chat_id, text):
    session = user_sessions.get(chat_id, {"step": "START"})
    
    if text == "/start" or text == "ابدأ" or session["step"] == "START":
        user_sessions[chat_id] = {"step": "WAIT_PHONE"}
        send_text(chat_id, "⚡ مرحباً بك في بوت نوتي برو!\n\nأرسل رقم هاتفك (07 / 06 / 05) لتسجيل الدخول:")
        
    elif session["step"] == "WAIT_PHONE":
        if len(text) == 10 and text.isdigit():
            user_sessions[chat_id] = {"step": "WAIT_OTP", "phone": text}
            send_text(chat_id, f"📩 تم إرسال رمز التحقق (OTP) إلى {text}.\nأدخل الرمز الآن:")
        else:
            send_text(chat_id, "❌ رقم غير صحيح، يرجى إرسال 10 أرقام:")
            
    elif session["step"] == "WAIT_OTP":
        user_sessions[chat_id]["step"] = "LOGGED_IN"
        send_menu(chat_id)

def handle_button(chat_id, data):
    if data == "GET_GIFT":
        send_text(chat_id, "⏳ جاري تفعيل الهدية الأسبوعية على شريحتك...")
    elif data == "CHECK_BALANCE":
        send_text(chat_id, "📊 جاري جلب تفاصيل الرصيد والإنترنت المتبقي...")
    elif data == "CHANGE_NUM":
        user_sessions[chat_id] = {"step": "WAIT_PHONE"}
        send_text(chat_id, "🔄 أرسل رقم الهاتف الجديد (10 أرقام):")

def send_text(chat_id, text):
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def send_menu(chat_id):
    url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "✅ تم الدخول بنجاح! اختر الخدمة المطلوبة من القائمة:",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🎁 تفعيل الهدية الأسبوعية", "callback_data": "GET_GIFT"}],
                [{"text": "💳 كشف الرصيد والإنترنت", "callback_data": "CHECK_BALANCE"}],
                [{"text": "🔄 تغيير رقم الهاتف", "callback_data": "CHANGE_NUM"}]
            ]
        }
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(port=5000)
