import os
import json
import urllib.request
from flask import Flask, request

app = Flask(__name__)

BOT_ID = "9232668538"
BOT_KEY = "AAFX3FgNFi6n9JB5eBd-ZUaJD8GFdU_1NWs"

PROTO = "https" + "://"
HOST = "api" + "." + "telegram" + "." + "org"
API_URL = PROTO + HOST + "/bot" + BOT_ID + ":" + BOT_KEY

# قاعدة بيانات الإجراءات الإدارية الأكثر طلباً في الجزائر
PROCEDURES = {
    "passport": {
        "title": "🛂 جواز السفر البيومتري",
        "docs": (
            "• استمارة مملوءة وممضاة (تُطبع من موقع وزارة الداخلية).\n"
            "• شهادة الميلاد رقم 12-خ (S12) الأصلية.\n"
            "• شهادة الإقامة يقل تاريخ إصدارها عن 3 أشهر.\n"
            "• شهادة العمل أو شهادة مدرسية (للطلبة) أو شهادة البطالة.\n"
            "• قسيمة جبائية (Timbre) بقيمة **6000 دج** (48 صفحة) أو **3000 دج** (للقصر والطلبة).\n"
            "• 02 صور شمسية بيومترية بخلفية بيضاء.\n"
            "• نسخة من بطاقة فصيلة الدم."
        ),
        "tip": "💡 **نصيحة:** في حالة التجديد، أحضر جواز السفر القديم، وإذا كان ضائعاً أرفق تصريح بالضياع من الشرطة + طابع 10000 دج إضافي."
    },
    "carte_grise": {
        "title": "🚗 البطاقة الرمادية (ترقيم سيارة جديدة/مستعملة)",
        "docs": (
            "• عقد البيع مصادق عليه في البلدية (أو فاتورة الشراء من الوكيل).\n"
            "• البطاقة الرمادية القديمة مشطوبة (في حالة سيارة مستعملة).\n"
            "• شهادة المراقبة التقنية للسيارات (Scanner) سارية المفعول.\n"
            "• بطاقة الإقامة + نسخة من بطاقة التعريف البيومترية.\n"
            "• وصل دفع قسيمة السيارات + الطابع الجبائي حسب قوة المحرك."
        ),
        "tip": "💡 **نصيحة:** تأكد من تطابق رقم الهيكل (Numéro de châssis) في العقد مع البطاقة الرمادية قبل المصادقة في البلدية."
    },
    "chomage": {
        "title": "💼 ملف منحة البطالة (ANEM)",
        "docs": (
            "• التسجيل الأولي عبر منصة **منحة (Minha)** وحجز موعد.\n"
            "• وصل الموعد المستخرج من المنصة + تعهد شرفي ممضى.\n"
            "• شهادة ميلاد + شهادة عائلية (للمتزوجين).\n"
            "• صك بريدي مشطوب (Chèque barré) باسم المعني.\n"
            "• نسخة من الشهادة الجامعية أو التكوين المهني (إن وجدت).\n"
            "• وثيقة إثبات الوضعية تجاه الخدمة الوطنية (للذكور)."
        ),
        "tip": "💡 **نصيحة:** يجب أن يكون حسابك البريدي (CCP) نشطاً وبنفس الاسم واللقب المسجلين في بطاقة التعريف البيومترية."
    },
    "casier": {
        "title": "⚖️ صحيفة السوابق القضائية (رقم 03)",
        "docs": (
            "• لا تحتاج للتنقل للمحكمة! تُستخرج مجاناً عبر الإنترنت.\n"
            "• ادخل لموقع وزارة العدل (**portail.mjustice.dz**).\n"
            "• أدخل رقم التعريف الوطني (NIN) ورقم بطاقة التعريف البيومترية.\n"
            "• ستصلك رسالة SMS برمز التحقق لتحميلها بصيغة PDF موقعة إلكترونياً."
        ),
        "tip": "💡 **نصيحة:** النسخة المستخرجة من الإنترنت صالحة ومقبولة قانوناً في جميع الإدارات والمسابقات دون الحاجة لختم المحكمة."
    },
    "chifa": {
        "title": "🏥 بطاقة الشفاء (CNAS) لأول مرة",
        "docs": (
            "• شهادة الانتساب (Attestation d'affiliation) يستخرجها رب العمل أو تُطبع من فضاء الهناء.\n"
            "• شهادة ميلاد + شهادة عائلية (للمتزوجين).\n"
            "• صورة شمسية حديثة بخلفية فاتحة.\n"
            "• نسخة من بطاقة التعريف البيومترية + شهادة فصيلة الدم."
        ),
        "tip": "💡 **نصيحة:** يمكنك الآن طلب بطاقة الشفاء ومتابعة جاهزيتها عن بُعد عبر تطبيق أو منصة **فضاء الهناء (El Hanaa)**."
    },
    "registre": {
        "title": "🏪 فتح سجل تجاري (شخص طبيعي)",
        "docs": (
            "• عقد ملكية المحل أو عقد كراء موثق (ساري المفعول).\n"
            "• شهادة ميلاد + شهادة إقامة.\n"
            "• وصل دفع حقوق التسجيل في السجل التجاري (CNRC).\n"
            "• الطابع الجبائي بقيمة **4000 دج**.\n"
            "• رخصة مسبقة (فقط للنشاطات المقننة مثل الصيدليات أو المقاهي)."
        ),
        "tip": "💡 **نصيحة:** بعد استلام السجل التجاري، لديك مهلة 10 أيام للتصريح بالوجود لدى مفتشية الضرائب وصندوق CASNOS لتفادي الغرامات."
    }
}

community_notes = []
waiting_note = {}

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

def main_keyboard():
    return [
        [{"text": "🛂 جواز السفر البيومتري", "callback_data": "proc_passport"}, {"text": "🚗 البطاقة الرمادية", "callback_data": "proc_carte_grise"}],
        [{"text": "💼 منحة البطالة (ANEM)", "callback_data": "proc_chomage"}, {"text": "⚖️ السوابق القضائية", "callback_data": "proc_casier"}],
        [{"text": "🏥 بطاقة الشفاء (CNAS)", "callback_data": "proc_chifa"}, {"text": "🏪 فتح سجل تجاري", "callback_data": "proc_registre"}],
        [{"text": "📢 تجارب المواطنين اليوم", "callback_data": "view_notes"}, {"text": "✍️ أضف معلومة إدارية", "callback_data": "add_note"}]
    ]

@app.route('/')
def home():
    my_site = PROTO + "bot-dz-qob9" + "." + "onrender" + "." + "com" + "/webhook"
    res = tg_request("setWebhook?url=" + my_site)
    return "Moussa3id Idari DZ Status: " + str(res)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return "OK", 200

    if "message" in data and "text" in data["message"]:
        cid = data["message"]["chat"]["id"]
        txt = data["message"]["text"].strip()
        name = data["message"]["from"].get("first_name", "مواطن")

        if waiting_note.get(cid) and txt != "/start":
            waiting_note[cid] = False
            community_notes.insert(0, f"👤 **{name}:** {txt[:150]}")
            if len(community_notes) > 10:
                community_notes.pop()
            send_msg(cid, "✅ **يعطيك الصحة! تمت مشاركة تجربتك مع باقي المواطنين.**", main_keyboard())
            return "OK", 200

        waiting_note[cid] = False
        welcome = (
            f"🇩🇿 **أهلاً بك يا {name} في (مُساعدك الإداري DZ)!**\n\n"
            "🛑 **ما تزيدش تضيع نهارك في الإدارة على جال ورقة ناقصة!**\n"
            "اختر الوثيقة أو الإجراء الذي تريده لمعرفة **الملف الكامل + الطابع الجبائي + أسرار القبول السريع**:"
        )
        send_msg(cid, welcome, main_keyboard())

    elif "callback_query" in data:
        call = data["callback_query"]
        cid = call["message"]["chat"]["id"]
        mid = call["message"]["message_id"]
        cdata = call["data"]
        tg_request("answerCallbackQuery", {"callback_query_id": call["id"]})

        if cdata.startswith("proc_"):
            key = cdata.replace("proc_", "")
            item = PROCEDURES.get(key)
            if item:
                text = f"**{item['title']}**\n\n📋 **الوثائق المطلوبة:**\n{item['docs']}\n\n{item['tip']}"
                btns = [[{"text": "🔙 رجوع لقائمة الوثائق", "callback_data": "back_home"}]]
                edit_msg(cid, mid, text, btns)

        elif cdata == "view_notes":
            if not community_notes:
                notes_text = "📢 **لا توجد ملاحظات ميدانية مضافة اليوم بعد.**\nكن أول من يشارك تجربته في الإدارة لمساعدة إخوته!"
            else:
                notes_text = "📢 **آخر تحديثات وتجارب المواطنين في الإدارات:**\n\n" + "\n\n".join(community_notes)
            btns = [
                [{"text": "✍️ أضف تجربتك الآن", "callback_data": "add_note"}],
                [{"text": "🔙 رجوع للقائمة الرئيسية", "callback_data": "back_home"}]
            ]
            edit_msg(cid, mid, notes_text, btns)

        elif cdata == "add_note":
            waiting_note[cid] = True
            send_msg(cid, "✍️ **اكتب الآن ملاحظتك أو تجربتك اليوم في الإدارة** (مثال: *في دائرة وهران يطلبون نسخة إضافية من بطاقة التعريف لتجديد الباسبور*):")

        elif cdata == "back_home":
            edit_msg(cid, mid, "👇 **اختر الوثيقة أو الإجراء الإداري الذي تبحث عنه:**", main_keyboard())

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
