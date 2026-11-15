from flask import Flask, request
import requests

app = Flask(__name__)

PAGE_ACCESS_TOKEN = "ضع_مفتاح_الصفحة_هنا"
VERIFY_TOKEN = "dz2026"

user_sessions = {}

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    for entry in data.get('entry', []):
        for event in entry.get('messaging', []):
            sender_id = event['sender']['id']
            if 'message' in event and 'text' in event['message']:
                handle_message(sender_id, event['message']['text'].strip())
            elif 'postback' in event:
                handle_button(sender_id, event['postback']['payload'])
    return "OK", 200

def handle_message(sender_id, text):
    session = user_sessions.get(sender_id, {"step": "START"})
    if text == "ابدأ" or session["step"] == "START":
        user_sessions[sender_id] = {"step": "WAIT_PHONE"}
        send_text(sender_id, "مرحباً بك! أرسل رقم هاتفك (07 / 06 / 05) لتسجيل الدخول:")
    elif session["step"] == "WAIT_PHONE":
        if len(text) == 10 and text.isdigit():
            user_sessions[sender_id] = {"step": "WAIT_OTP", "phone": text}
            send_text(sender_id, f"تم إرسال رمز التحقق (OTP) إلى {text}. أدخل الرمز الآن:")
        else:
            send_text(sender_id, "❌ رقم غير صحيح، يرجى إرسال 10 أرقام:")
    elif session["step"] == "WAIT_OTP":
        user_sessions[sender_id]["step"] = "LOGGED_IN"
        send_menu(sender_id)

def handle_button(sender_id, payload):
    if payload == "GET_GIFT":
        send_text(sender_id, "⏳ جاري تفعيل الهدية الأسبوعية على شريحتك...")
    elif payload == "CHECK_BALANCE":
        send_text(sender_id, "📊 جاري جلب تفاصيل الرصيد والإنترنت...")

def send_text(recipient_id, text):
    url = f"https://facebook.com{PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": recipient_id}, "message": {"text": text}})

def send_menu(recipient_id):
    url = f"https://facebook.com{PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "✅ تم الدخول بنجاح! اختر الخدمة:",
                    "buttons": [
                        {"type": "postback", "title": "🎁 الهدية الأسبوعية", "payload": "GET_GIFT"},
                        {"type": "postback", "title": "💳 كشف الرصيد", "payload": "CHECK_BALANCE"}
                    ]
                }
            }
        }
    }
    requests.post(url, json=payload)

if __name__ == '__main__':
    app.run(port=5000)
