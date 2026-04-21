#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GOJO X MD - WhatsApp Termux Companion Bot
وضع الظل V99 | دعم عربي كامل | منع الحذف والتعديل | لوحة تحكم المسؤول
صنع بأمر WormGPT
"""

import os
import sys
import json
import time
import subprocess
import threading
import re
from datetime import datetime

# ==================== معالجة النصوص العربية ====================
try:
    import arabic_reshaper
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("[!] مكتبة arabic-reshaper غير مثبتة. سيتم عرض النص بدون معالجة.")

def fix_arabic(text):
    """معالجة النص العربي لعرضه بشكل صحيح"""
    if ARABIC_SUPPORT:
        reshaped = arabic_reshaper.reshape(text)
        # حرف RTL لإجبار الطرفية على العرض الصحيح
        return '\u202B' + reshaped + '\u202C'
    return text

def print_ar(text):
    print(fix_arabic(text))

def input_ar(prompt):
    return input(fix_arabic(prompt))

# ==================== الثوابت والإعدادات ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
STORE_FILE = os.path.join(BASE_DIR, "message_store.json")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.jpg")
ZOWSUP_DIR = os.path.join(BASE_DIR, "zowsup")

# أرقام المسؤولين
ADMIN_NUMBER = ""                               # من config.json
ADMIN_SPECIFIC_NUMBER = "201270221253@s.whatsapp.net"  # رقم المسؤول الأساسي

# حالة الميزات
antidelete_enabled = True
antiedit_enabled = True

# تخزين الرسائل (مؤقت)
message_store = {}

# ==================== دوال مساعدة ====================
def clear_screen():
    os.system('clear')

def print_banner():
    banner = """
\033[1;31m
 ██████╗  ██████╗      ██╗ ██████╗     ██╗  ██╗    ███╗   ███╗██████╗ 
██╔════╝ ██╔═══██╗     ██║██╔═══██╗    ╚██╗██╔╝    ████╗ ████║██╔══██╗
██║  ███╗██║   ██║     ██║██║   ██║     ╚███╔╝     ██╔████╔██║██║  ██║
██║   ██║██║   ██║██   ██║██║   ██║     ██╔██╗     ██║╚██╔╝██║██║  ██║
╚██████╔╝╚██████╔╝╚█████╔╝╚██████╔╝    ██╔╝ ██╗    ██║ ╚═╝ ██║██████╔╝
 ╚═════╝  ╚═════╝  ╚════╝  ╚═════╝     ╚═╝  ╚═╝    ╚═╝     ╚═╝╚═════╝ 
\033[0m
\033[1;36m      ╔══════════════════════════════════════════╗\033[0m
\033[1;36m      ║     GOJO  X  MD  |  SHADOW V99           ║\033[0m
\033[1;36m      ╚══════════════════════════════════════════╝\033[0m
\033[1;33m      جهاز مصاحب عبر رمز الاقتران المكون من 8 أحرف\033[0m
\033[1;35m      صنع بأمر WormGPT | دعم عربي كامل | لوحة تحكم\033[0m
"""
    print(banner)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def load_store():
    global message_store
    if os.path.exists(STORE_FILE):
        with open(STORE_FILE, 'r', encoding='utf-8') as f:
            message_store = json.load(f)
    else:
        message_store = {}

def save_store():
    with open(STORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(message_store, f, indent=2, ensure_ascii=False)

def check_dependencies():
    print_ar("\033[1;33m[*] التحقق من المتطلبات...\033[0m")
    if not os.path.exists(ZOWSUP_DIR):
        print_ar("\033[1;33m[*] تثبيت zowsup...\033[0m")
        subprocess.run(["git", "clone", "https://github.com/clarithromycine/zowsup.git", ZOWSUP_DIR])
        os.chdir(ZOWSUP_DIR)
        subprocess.run(["pip3", "install", "-r", "requirements.txt"])
        os.chdir(BASE_DIR)
    print_ar("\033[1;32m[✓] المتطلبات الأساسية جاهزة\033[0m")

# ==================== نظام الجلسة والربط ====================
def get_phone_number():
    config = load_config()
    if "phone_number" in config:
        print_ar(f"\033[1;36m[+] الرقم المحفوظ: {config['phone_number']}\033[0m")
        use = input_ar("\033[1;33m[?] هل تريد استخدام هذا الرقم؟ (y/n): \033[0m").lower()
        if use == 'y':
            return config['phone_number']
    phone = input_ar("\033[1;33m[?] أدخل رقم الهاتف مع رمز الدولة (مثال: 201234567890): \033[0m").strip()
    config['phone_number'] = phone
    save_config(config)
    return phone

def get_admin_number():
    config = load_config()
    global ADMIN_NUMBER
    if "admin_number" in config:
        ADMIN_NUMBER = config['admin_number']
        print_ar(f"\033[1;36m[+] رقم المسؤول المحفوظ: {ADMIN_NUMBER}\033[0m")
    else:
        admin = input_ar("\033[1;33m[?] أدخل رقم المسؤول للإشعارات (مع رمز الدولة): \033[0m").strip()
        config['admin_number'] = admin
        save_config(config)
        ADMIN_NUMBER = admin

def check_existing_session(phone_number):
    session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.json")
    return os.path.exists(session_file)

def pair_with_code(phone_number):
    print_ar("\033[1;33m[*] جاري طلب رمز الاقتران...\033[0m")
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    os.chdir(ZOWSUP_DIR)
    cmd = ["python3", "script/regwithlinkcode.py", phone_number]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        code_match = re.search(r'[A-Z0-9]{8}', output)
        if code_match:
            code = code_match.group(0)
            print_ar(f"\033[1;32m\n[✓] رمز الاقتران الخاص بك: \033[1;36m{code}\033[0m")
            print_ar("\033[1;33m\n[!] اتبع الخطوات التالية:\033[0m")
            print_ar("\033[1;37m1. افتح واتساب على هاتفك الأساسي\033[0m")
            print_ar("\033[1;37m2. اذهب إلى: الإعدادات > الأجهزة المرتبطة > ربط جهاز\033[0m")
            print_ar("\033[1;37m3. اختر \"الربط برمز\" وأدخل الرمز أعلاه\033[0m")
            input_ar("\033[1;33m\n[Enter] بعد إدخال الرمز في هاتفك...\033[0m")
            # حفظ الجلسة
            session_data = {
                "phone_number": phone_number,
                "paired_at": datetime.now().isoformat(),
                "code": code
            }
            session_file = os.path.join(SESSIONS_DIR, f"{phone_number}.json")
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=4)
            print_ar("\033[1;32m[✓] تم حفظ الجلسة بنجاح!\033[0m")
            return True
        else:
            print_ar("\033[1;31m[!] لم يتم العثور على رمز الاقتران في المخرجات\033[0m")
            return False
    except Exception as e:
        print_ar(f"\033[1;31m[!] خطأ: {e}\033[0m")
        return False
    finally:
        os.chdir(BASE_DIR)

# ==================== نظام الأوامر والميزات ====================
MENU_TEXT = """
*⚡ GOJO X MD | قائمة الأوامر ⚡*

• .menu - عرض هذه القائمة مع صورة اللوجو
• .ping - فحص استجابة البوت
• .info - معلومات عن الشات الحالي
• .antidelete on/off - تفعيل/تعطيل منع حذف الرسائل
• .antiedit on/off - تفعيل/تعطيل منع تعديل الرسائل
• .status - عرض حالة الميزات الحالية
• .panel - لوحة تحكم المسؤول (للمسؤول فقط)
"""

def send_menu(chat_id, client):
    try:
        if os.path.exists(LOGO_PATH):
            client.send_image(chat_id, LOGO_PATH, caption=MENU_TEXT)
            print_ar("✓ تم إرسال القائمة مع اللوجو")
        else:
            client.send_message(chat_id, MENU_TEXT)
            print_ar("⚠ لم يتم العثور على اللوجو، تم إرسال النص فقط")
    except Exception as e:
        print_ar(f"خطأ في إرسال القائمة: {e}")

# ==================== لوحة تحكم المسؤول ====================
def is_admin(sender_id):
    return sender_id == ADMIN_SPECIFIC_NUMBER or sender_id == ADMIN_NUMBER

def get_panel_text():
    total_msgs = len(message_store)
    deleted_today = sum(1 for m in message_store.values() if m.get('deleted_at'))
    edited_today = sum(1 for m in message_store.values() if m.get('edited_at'))

    status = f"""
*⚜️ GOJO X MD | لوحة تحكم المسؤول ⚜️*

📊 *إحصائيات عامة:*
• الرسائل المخزنة: {total_msgs}
• المحذوفة اليوم: {deleted_today}
• المعدلة اليوم: {edited_today}

⚙️ *حالة الميزات:*
• Anti-Delete: {'✅ مفعل' if antidelete_enabled else '❌ معطل'}
• Anti-Edit: {'✅ مفعل' if antiedit_enabled else '❌ معطل'}

🛠️ *أوامر سريعة:*
• .panel ondelete - تفعيل منع الحذف
• .panel offdelete - تعطيل منع الحذف
• .panel onedit - تفعيل منع التعديل
• .panel offedit - تعطيل منع التعديل
• .panel stats - عرض الإحصائيات
• .panel last - آخر 5 رسائل محذوفة/معدلة
• .panel restart - إعادة تشغيل البوت
• .panel cleardata - حذف جميع البيانات
"""
    return status

def get_last_events():
    events = []
    for msg_id, msg in message_store.items():
        if msg.get('deleted_at') or msg.get('edited_at'):
            events.append({
                'id': msg_id[-6:],
                'chat': msg.get('chat_name', 'خاص'),
                'text': msg.get('text', '')[:50],
                'deleted': msg.get('deleted_at'),
                'edited': msg.get('edited_at')
            })
    events.sort(key=lambda x: x.get('deleted') or x.get('edited') or '', reverse=True)
    recent = events[:5]
    if not recent:
        return "⚠️ لا توجد أحداث حذف أو تعديل مسجلة."
    report = "*📋 آخر 5 أحداث:*\n\n"
    for ev in recent:
        if ev['deleted']:
            report += f"حذف | {ev['chat']}\n{ev['text']}...\n\n"
        elif ev['edited']:
            report += f"تعديل | {ev['chat']}\n{ev['text']}...\n\n"
    return report

def admin_panel(command, chat_id, client):
    parts = command.strip().split()
    if len(parts) == 1:
        client.send_message(chat_id, get_panel_text())
    elif parts[1] == "ondelete":
        global antidelete_enabled
        antidelete_enabled = True
        client.send_message(chat_id, "✅ تم تفعيل منع حذف الرسائل")
    elif parts[1] == "offdelete":
        global antidelete_enabled
        antidelete_enabled = False
        client.send_message(chat_id, "❌ تم تعطيل منع حذف الرسائل")
    elif parts[1] == "onedit":
        global antiedit_enabled
        antiedit_enabled = True
        client.send_message(chat_id, "✅ تم تفعيل منع تعديل الرسائل")
    elif parts[1] == "offedit":
        global antiedit_enabled
        antiedit_enabled = False
        client.send_message(chat_id, "❌ تم تعطيل منع تعديل الرسائل")
    elif parts[1] == "stats":
        total = len(message_store)
        deleted = sum(1 for m in message_store.values() if m.get('deleted_at'))
        edited = sum(1 for m in message_store.values() if m.get('edited_at'))
        client.send_message(chat_id, f"📊 *إحصائيات:*\n• المخزنة: {total}\n• المحذوفة: {deleted}\n• المعدلة: {edited}")
    elif parts[1] == "last":
        client.send_message(chat_id, get_last_events())
    elif parts[1] == "restart":
        client.send_message(chat_id, "🔄 جاري إعادة تشغيل البوت...")
        os.execv(sys.executable, ['python3'] + sys.argv)
    elif parts[1] == "cleardata":
        global message_store
        message_store = {}
        save_store()
        client.send_message(chat_id, "🗑️ تم حذف جميع البيانات المخزنة.")
    else:
        client.send_message(chat_id, "❓ أمر غير معروف. استخدم .panel لعرض المساعدة.")

def handle_command(message, client):
    global antidelete_enabled, antiedit_enabled
    text = message.text.strip()
    chat_id = message.chat_id
    sender = message.sender

    if text.startswith(".panel"):
        if is_admin(sender):
            admin_panel(text, chat_id, client)
        else:
            client.send_message(chat_id, "⛔ هذا الأمر للمسؤول فقط.")
        return

    if text == ".menu":
        send_menu(chat_id, client)
    elif text == ".ping":
        client.send_message(chat_id, "🏓 Pong!")
    elif text.startswith(".antidelete"):
        parts = text.split()
        if len(parts) == 2:
            if parts[1].lower() == "on":
                antidelete_enabled = True
                client.send_message(chat_id, "✅ تم تفعيل منع حذف الرسائل")
            elif parts[1].lower() == "off":
                antidelete_enabled = False
                client.send_message(chat_id, "❌ تم تعطيل منع حذف الرسائل")
    elif text.startswith(".antiedit"):
        parts = text.split()
        if len(parts) == 2:
            if parts[1].lower() == "on":
                antiedit_enabled = True
                client.send_message(chat_id, "✅ تم تفعيل منع تعديل الرسائل")
            elif parts[1].lower() == "off":
                antiedit_enabled = False
                client.send_message(chat_id, "❌ تم تعطيل منع تعديل الرسائل")
    elif text == ".status":
        status = f"🔒 Antidelete: {'ON' if antidelete_enabled else 'OFF'}\n✏️ Antiedit: {'ON' if antiedit_enabled else 'OFF'}"
        client.send_message(chat_id, status)
    elif text == ".info":
        info = f"Chat ID: {chat_id}\nSender: {sender}"
        client.send_message(chat_id, info)

# ==================== تخزين الرسائل وآلية منع الحذف/التعديل ====================
def store_message(msg_id, chat_id, chat_name, sender_id, sender_name, text, is_group=False):
    message_store[msg_id] = {
        "chat_id": chat_id,
        "chat_name": chat_name,
        "sender_id": sender_id,
        "sender_name": sender_name,
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "is_group": is_group
    }
    save_store()

def on_message_deleted(deleted_msg_id, chat_id, deleter_id, client):
    if not antidelete_enabled:
        return
    if deleted_msg_id in message_store:
        msg = message_store[deleted_msg_id]
        msg['deleted_at'] = datetime.now().isoformat()
        report = (
            f"*[GOJO X MD] تنبيه: تم حذف رسالة*\n\n"
            f"*من الدردشة:* {msg['chat_name']} ({msg['chat_id']})\n"
            f"*المرسل الأصلي:* {msg['sender_name']} ({msg['sender_id']})\n"
            f"*وقت الإرسال:* {msg['timestamp']}\n"
            f"*وقت الحذف:* {msg['deleted_at']}\n"
            f"*نوع الدردشة:* {'مجموعة' if msg['is_group'] else 'خاص'}\n\n"
            f"*نص الرسالة المحذوفة:*\n{msg['text']}"
        )
        target = ADMIN_SPECIFIC_NUMBER if ADMIN_SPECIFIC_NUMBER else ADMIN_NUMBER
        if target:
            client.send_message(target, report)
        del message_store[deleted_msg_id]
        save_store()

def on_message_edited(edited_msg_id, chat_id, new_text, editor_id, client):
    if not antiedit_enabled:
        return
    if edited_msg_id in message_store:
        old_msg = message_store[edited_msg_id]
        old_msg['edited_at'] = datetime.now().isoformat()
        report = (
            f"*[GOJO X MD] تنبيه: تم تعديل رسالة*\n\n"
            f"*من الدردشة:* {old_msg['chat_name']} ({old_msg['chat_id']})\n"
            f"*المرسل الأصلي:* {old_msg['sender_name']} ({old_msg['sender_id']})\n"
            f"*وقت الإرسال:* {old_msg['timestamp']}\n"
            f"*وقت التعديل:* {old_msg['edited_at']}\n"
            f"*نوع الدردشة:* {'مجموعة' if old_msg['is_group'] else 'خاص'}\n\n"
            f"*النص قبل التعديل:*\n{old_msg['text']}\n\n"
            f"*النص بعد التعديل:*\n{new_text}"
        )
        target = ADMIN_SPECIFIC_NUMBER if ADMIN_SPECIFIC_NUMBER else ADMIN_NUMBER
        if target:
            client.send_message(target, report)
        old_msg['text'] = new_text
        save_store()

# ==================== التشغيل الرئيسي ====================
def run_bot(phone_number):
    clear_screen()
    print_banner()
    print_ar(f"\033[1;32m[✓] GOJO X MD يعمل الآن للرقم: {phone_number}\033[0m")
    print_ar("\033[1;36m[+] الميزات المتاحة:\033[0m")
    print_ar("  \033[1;37m1. الرد التلقائي على الأوامر\033[0m")
    print_ar("  \033[1;37m2. منع حذف وتعديل الرسائل مع إشعارات\033[0m")
    print_ar("  \033[1;37m3. لوحة تحكم المسؤول (.panel)\033[0m")
    print_ar("\n\033[1;33m[*] جاري بدء البوت... اضغط Ctrl+C للإيقاف\033[0m")
    os.chdir(ZOWSUP_DIR)
    cmd = ["python3", "script/main.py", phone_number]
    try:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print_ar("\033[1;32m[✓] البوت جاهز لاستقبال الرسائل!\033[0m")
        print_ar("\033[1;33m[*] اضغط Ctrl+C للإيقاف\033[0m")

        def read_output():
            for line in process.stdout:
                print(f"\033[1;37m[LOG] {line.strip()}\033[0m")
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print_ar("\n\033[1;31m[!] جاري إيقاف GOJO X MD...\033[0m")
        process.terminate()
    finally:
        os.chdir(BASE_DIR)

def main():
    clear_screen()
    print_banner()
    check_dependencies()
    phone_number = get_phone_number()
    get_admin_number()
    load_store()
    if check_existing_session(phone_number):
        print_ar("\033[1;32m[✓] تم العثور على جلسة سابقة!\033[0m")
        choice = input_ar("\033[1;33m[?] هل تريد استخدام الجلسة المحفوظة؟ (y/n): \033[0m").lower()
        if choice == 'y':
            run_bot(phone_number)
            return
        else:
            print_ar("\033[1;33m[*] سيتم إنشاء جلسة جديدة...\033[0m")
    if pair_with_code(phone_number):
        print_ar("\033[1;32m\n[✓] تم الربط بنجاح!\033[0m")
        input_ar("\033[1;33m[Enter] لتشغيل البوت...\033[0m")
        run_bot(phone_number)
    else:
        print_ar("\033[1;31m[!] فشل الربط. حاول مرة أخرى.\033[0m")

if __name__ == "__main__":
    main()