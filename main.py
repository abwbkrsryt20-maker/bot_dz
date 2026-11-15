import os
import json
import time
import urllib.request
from flask import Flask, request

app = Flask(__name__)

BOT_ID = "9232668538"
BOT_KEY = "AAEwX6AWbxuDu5MxGtFpf5tXZMVbAp3NcSo"
ADMIN_ID = 123456789

PROTO = "https" + "://"
HOST = "api" + "." + "telegram" + "." + "org"
API_URL = PROTO + HOST + "/bot" + BOT_ID + ":" + BOT_KEY

users = {}
waiting_phone = {}

def get_user(cid):
    if cid not in users:
        users[cid] = {"points": 0, "invites": 0, "last_weekly": 0}
    return users[cid]

def tg_request(method, data=None):
    url = API_URL + "/" + method
    if data:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
    else:
        req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as res:
            return res.read().decode('utf-8')
    except Exception as e:
        return str(e)

def send_msg(cid, text, buttons=None):
    payload = {"chat_id": cid, "text": text, "parse_mode": "Markdown"}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    tg_request("sendMessage", payload)

def main_buttons():
    return [
        [{"text": "🎁 الجائزة الأسبوعية (+20 نقطة)", "callback_data": "weekly"}],
        [{"text": "👥 رابط الدعوة (+10 نقاط)", "callback_data": "invite"}, {"text": "💰 نقاطي", "callback_data": "points"}],
        [{"text": "🏆 سحب جائزة 2 جيغا (100 نقطة)", "callback_data": "redeem"}]
    ]

@app.route('/')
def home():
    my_site = PROTO + "bot-dz-qob9" + "." + "onrender" + "." + "com" + "/webhook"
    res = tg_request("setWebhook?url=" + my_site)
    return "Bot Status: " + str(res)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return "OK", 200

    if "message" in data and "text" in data["message"]:
        cid = data["message"]["chat"]["id"]
        txt = data["message"]["text"].strip()
        name = data["message"]["from"].get("first_name", "صديقي")

        if waiting_phone.get(cid):
            if len(txt) == 10 and txt.isdigit() and txt.startswith(("05", "06", "07")):
                users[cid]["points"] -= 100
                waiting_phone[cid] = False
                send_msg(cid, f"✅ **تم استلام رقمك ({txt}) بنجاح!**\nسيتم إرسال جائزة **2 جيغا إنترنت** إليك قريباً.")
                send_msg(ADMIN_ID, f"🚨 **فائز جديد بجائزة 2 جيغا!**\n👤 الاسم: {name}\n📱 الرقم: `{txt}`")
            else:
                send_msg(cid, "❌ رقم غير صحيح! أرسل رقماً جزائرياً من 10 أرقام (05 / 06 / 07):")
            return "OK", 200

        is_new = cid not in users
        get_user(cid)
        parts = txt.split()
        if is_new and len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != cid and inviter in users:
                users[inviter]["points"] += 10
                users[inviter]["invites"] += 1
                send_msg(inviter, "🎉 **مبروك!** دخل صديق عبر رابطك وحصلت على **+10 نقاط**!")

        welcome = f"👋 **أهلاً بك يا {name} في بوت Noti Pro!**\n\nاجمع النقاط مجاناً واستبدلها بـ **2 جيغا إنترنت أو رصيد فليكسي**:"
        send_msg(cid, welcome, main_buttons())

    elif "callback_query" in data:
        call = data["callback_query"]
        cid = call["message"]["chat"]["id"]
        cdata = call["data"]
        user = get_user(cid)
        tg_request("answerCallbackQuery", {"callback_query_id": call["id"]})

        if cdata == "weekly":
            now = time.time()
            if now - user["last_weekly"] >= 604800:
                user["points"] += 20
                user["last_weekly"] = now
                send_msg(cid, "🎉 **مبروك!** حصلت على **جائزتك الأسبوعية (+20 نقطة)**!", main_buttons())
            else:
                days = int((604800 - (now - user["last_weekly"])) / 86400) + 1
                send_msg(cid, f"⏳ لقد أخذت جائزتك هذا الأسبوع.\nعُد بعد **{days} أيام**.", main_buttons())

        elif cdata == "invite":
            link = PROTO + "t.me/noti_dz_2027_bot?start=" + str(cid)
            send_msg(cid, f"👥 **شارك رابطك واربح 10 نقاط عن كل صديق:**\n\n`{link}`", main_buttons())

        elif cdata == "points":
            send_msg(cid, f"💰 **نقاطك الحالية:** {user['points']} نقطة\n👥 **عدد الدعوات:** {user['invites']}\n🎯 **المطلوب لـ 2 جيغا:** 100 نقطة", main_buttons())

        elif cdata == "redeem":
            if user["points"] >= 100:
                waiting_phone[cid] = True
                send_msg(cid, "📱 **مبروك وصولك لـ 100 نقطة!**\nأرسل الآن **رقم هاتفك** (10 أرقام) لشحن 2 جيغا إنترنت:")
            else:
                send_msg(cid, f"❌ نقاطك الحالية **{user['points']}** فقط. اجمع **100 نقطة** لطلب الجائزة!", main_buttons())

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
