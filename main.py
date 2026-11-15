import os
import json
import time
import urllib.request
from flask import Flask, request

app = Flask(__name__)

# إعدادات البوت
BOT_ID = "9232668538"
BOT_KEY = "AAFX3FgNFi6n9JB5eBd-ZUaJD8GFdU_1NWs"

PROTO = "https" + "://"
HOST = "api" + "." + "telegram" + "." + "org"
API_URL = PROTO + HOST + "/bot" + BOT_ID + ":" + BOT_KEY

# قائمة الـ 58 ولاية جزائرية كاملة
WILAYAS = [
    "01 - أدرار", "02 - الشلف", "03 - الأغواط", "04 - أم البواقي", "05 - باتنة",
    "06 - بجاية", "07 - بسكرة", "08 - بشار", "09 - البليدة", "10 - البويرة",
    "11 - تمنراست", "12 - تبسة", "13 - تلمسان", "14 - تيارت", "15 - تيزي وزو",
    "16 - الجزائر العاصمة", "17 - الجلفة", "18 - جيجل", "19 - سطيف", "20 - سعيدة",
    "21 - سكيكدة", "22 - سيدي بلعباس", "23 - عنابة", "24 - قالمة", "25 - قسنطينة",
    "26 - المدية", "27 - مستغانم", "28 - المسيلة", "29 - معسكر", "30 - ورقلة",
    "31 - وهران", "32 - البيض", "33 - إليزي", "34 - برج بوعريريج", "35 - بومرداس",
    "36 - الطارف", "37 - تندوف", "38 - تيسمسيلت", "39 - الوادي", "40 - خنشلة",
    "41 - سوق أهراس", "42 - تيبازة", "43 - ميلة", "44 - عين الدفلى", "45 - النعامة",
    "46 - عين تموشنت", "47 - غرداية", "48 - غليزان", "49 - تيميمون", "50 - برج باجي مختار",
    "51 - أولاد جلال", "52 - بني عباس", "53 - عين صالح", "54 - عين قزام", "55 - تقرت",
    "56 - جانت", "57 - المغير", "58 - المنيعة"
]

reports = {
    "16 - الجزائر العاصمة": {
        "البريد المركزي (الجزائر الوسطى)": {"status": "🟡 كاين دراهم + طابور متوسط", "time": "منذ قليل", "user": "النظام"},
        "دائرة وبلدية باب الزوار": {"status": "🟢 كاين دراهم + فارغ", "time": "منذ قليل", "user": "النظام"},
        "دائرة بئر مراد رايس": {"status": "🟢 كاين دراهم + فارغ", "time": "منذ قليل", "user": "النظام"},
        "دائرة الرويبة": {"status": "🔴 طابور طويل جداً", "time": "منذ قليل", "user": "النظام"}
    },
    "31 - وهران": {
        "بريد وهران المركزي": {"status": "🟡 كاين دراهم + طابور متوسط", "time": "منذ قليل", "user": "النظام"},
        "دائرة السانيا": {"status": "🟢 كاين دراهم + فارغ", "time": "منذ قليل", "user": "النظام"},
        "دائرة بئر الجير": {"status": "🟢 كاين دراهم + فارغ", "time": "منذ قليل", "user": "النظام"}
    },
    "25 - قسنطينة": {
        "بريد قسنطينة المركزي": {"status": "🟢 كاين دراهم + فارغ", "time": "منذ قليل", "user": "النظام"},
        "دائرة الخروب (علي منجلي)": {"status": "🟡 كاين دراهم + طابور متوسط", "time": "منذ قليل", "user": "النظام"}
    },
    "19 - سطيف": {
        "بريد سطيف المركزي": {"status": "🔴 طابور طويل جداً", "time": "منذ قليل", "user": "النظام"},
        "دائرة العلمة": {"status": "🟢 كاين دراهم + فارغ", "time": "منذ قليل", "user": "النظام"}
    }
}

for w in WILAYAS:
    if w not in reports:
        w_name = w.split(" - ")[1]
        reports[w] = {
            f"البريد المركزي ({w_name})": {"status": "⚪ لا يوجد تحديث بعد (كن أول من يبلغ)", "time": "—", "user": "—"}
        }

user_state = {}

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

def edit_msg(cid, mid, text, buttons=None):
    payload = {"chat_id": cid, "message_id": mid, "text": text, "parse_mode": "Markdown"}
    if buttons:
        payload["reply_markup"] = {"inline_keyboard": buttons}
    tg_request("editMessageText", payload)

def wilayas_keyboard(page=0):
    per_page = 12
    start = page * per_page
    end = start + per_page
    slice_w = WILAYAS[start:end]

    buttons = []
    row = []
    for idx, w in enumerate(slice_w, start=start):
        row.append({"text": w, "callback_data": f"w_{idx}"})
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append({"text": "➡️ السابق", "callback_data": f"page_{page-1}"})
    if end < len(WILAYAS):
        nav.append({"text": "التالي ⬅️", "callback_data": f"page_{page+1}"})
    if nav:
        buttons.append(nav)

    return buttons

def communes_keyboard(w_idx):
    w_name = WILAYAS[w_idx]
    communes = list(reports[w_name].keys())
    buttons = []
    for c_idx, c_name in enumerate(communes):
        status_icon = reports[w_name][c_name]["status"].split()[0]
        buttons.append([{"text": f"{status_icon} {c_name}", "callback_data": f"c_{w_idx}_{c_idx}"}])

    buttons.append([{"text": "➕ إضافة دائرة / بلدية / مركز بريد جديد", "callback_data": f"addc_{w_idx}"}])
    buttons.append([{"text": "🔙 رجوع لقائمة الولايات (58 ولاية)", "callback_data": "page_0"}])
    return buttons

@app.route('/')
def home():
    my_site = PROTO + "bot-dz-qob9" + "." + "onrender" + "." + "com" + "/webhook"
    res = tg_request("setWebhook?url=" + my_site)
    return "Radar Poste DZ (58 Wilayas & Communes) Status: " + str(res)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return "OK", 200

    if "message" in data and "text" in data["message"]:
        cid = data["message"]["chat"]["id"]
        txt = data["message"]["text"].strip()
        name = data["message"]["from"].get("first_name", "مواطن")

        state = user_state.get(cid, {})
        if state.get("action") == "adding_commune" and txt != "/start":
            w_idx = state["w_idx"]
            w_name = WILAYAS[w_idx]
            new_commune = txt[:40]
            if new_commune not in reports[w_name]:
                reports[w_name][new_commune] = {
                    "status": "⚪ تمت الإضافة حديثاً (اختر الحالة بالأسفل)",
                    "time": time.strftime("%H:%M"),
                    "user": name
                }
            user_state[cid] = {}
            send_msg(
                cid,
                f"✅ **تمت إضافة ({new_commune}) بنجاح إلى ولاية {w_name}!**\n\n👇 اخترها الآن من القائمة لتحديث حالة السيولة والطابور فيها:",
                communes_keyboard(w_idx)
            )
            return "OK", 200

        user_state[cid] = {}
        welcome = (
            f"🇩🇿 **أهلاً بك يا {name} في رادار البريد DZ الشامل!**\n\n"
            "📍 يغطي جميع **الولايات (58)، الدوائر، البلديات ومراكز البريد** في الجزائر لحظة بلحظة.\n\n"
            "👇 **اختر ولايتك من القائمة بالأسفل:**"
        )
        send_msg(cid, welcome, wilayas_keyboard(0))

    elif "callback_query" in data:
        call = data["callback_query"]
        cid = call["message"]["chat"]["id"]
        mid = call["message"]["message_id"]
        cdata = call["data"]
        name = call["from"].get("first_name", "مواطن")
        tg_request("answerCallbackQuery", {"callback_query_id": call["id"]})

        if cdata.startswith("page_"):
            page = int(cdata.split("_")[1])
            edit_msg(cid, mid, f"🇩🇿 **اختر ولايتك (صفحة {page+1} من 5):**", wilayas_keyboard(page))

        elif cdata.startswith("w_"):
            w_idx = int(cdata.split("_")[1])
            w_name = WILAYAS[w_idx]
            text = (
                f"📍 **ولاية: {w_name}**\n\n"
                "👇 اختر **الدائرة / البلدية / مركز البريد** لمعرفة حالة السيولة والطابور، أو أضف بلديتك إذا لم تكن موجودة:"
            )
            edit_msg(cid, mid, text, communes_keyboard(w_idx))

        elif cdata.startswith("addc_"):
            w_idx = int(cdata.split("_")[1])
            w_name = WILAYAS[w_idx]
            user_state[cid] = {"action": "adding_commune", "w_idx": w_idx}
            send_msg(cid, f"✍️ **اكتب الآن اسم الدائرة أو البلدية أو مركز البريد** في ولاية **{w_name}** (مثال: *دائرة بئر العاتر* أو *بريد حي النصر*):")

        elif cdata.startswith("c_"):
            parts = cdata.split("_")
            w_idx = int(parts[1])
            c_idx = int(parts[2])
            w_name = WILAYAS[w_idx]
            c_name = list(reports[w_name].keys())[c_idx]
            info = reports[w_name][c_name]

            text = (
                f"🏛️ **الولاية:** {w_name}\n"
                f"📍 **الدائرة / البلدية:** {c_name}\n\n"
                f"📊 **الحالة الآن:** {info['status']}\n"
                f"🕒 **وقت التحديث:** {info['time']}\n"
                f"👤 **بواسطة:** {info['user']}\n\n"
                "👇 **هل أنت متواجد هناك الآن؟ حدّث الحالة بضغطة زر:**"
            )
            btns = [
                [{"text": "🟢 كاين دراهم + فارغ (لا يوجد طابور)", "callback_data": f"set_{w_idx}_{c_idx}_green"}],
                [{"text": "🟡 كاين دراهم + طابور متوسط", "callback_data": f"set_{w_idx}_{c_idx}_yellow"}],
                [{"text": "🔴 طابور طويل جداً (غاشي بزاف)", "callback_data": f"set_{w_idx}_{c_idx}_red"}],
                [{"text": "❌ لا توجد سيولة (خلاصو الدراهم)", "callback_data": f"set_{w_idx}_{c_idx}_empty"}],
                [{"text": "🔙 رجوع لدوائر وبلديات الولاية", "callback_data": f"w_{w_idx}"}]
            ]
            edit_msg(cid, mid, text, btns)

        elif cdata.startswith("set_"):
            parts = cdata.split("_")
            w_idx = int(parts[1])
            c_idx = int(parts[2])
            status_code = parts[3]

            w_name = WILAYAS[w_idx]
            c_name = list(reports[w_name].keys())[c_idx]

            status_map = {
                "green": "🟢 كاين دراهم + فارغ (لا يوجد طابور)",
                "yellow": "🟡 كاين دراهم + طابور متوسط",
                "red": "🔴 طابور طويل جداً (غاشي بزاف)",
                "empty": "❌ لا توجد سيولة (خلاصو الدراهم)"
            }
            current_time = time.strftime("%H:%M")
            reports[w_name][c_name] = {
status": status_map[status_code],
"time": f"اليوم على الساعة {current_time}",
"user": name
}
text = (
f"✅ يعطيك الصحة يا {name}!\n"
f"تم تحديث حالة {c_name} ({w_name}) بنجاح ليراها جميع المواطنين:\n\n"
f"📊 {status_map[status_code]}"
)
btns = [
[{"text": "🔙 رجوع لدوائر وبلديات الولاية", "callback_data": f"w_{w_idx}"}],
[{"text": "🏠 القائمة الرئيسية (58 ولاية)", "callback_data": "page_0"}]
]
edit_msg(cid, mid, text, btns)
return "OK", 200
if name == "main":
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
