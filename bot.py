import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import schedule
import time
import threading

# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'

# لیست آیدی‌های ادمین‌ها
ADMIN_USERS = [1891217517,6442428304]  # آیدی‌های ادمین‌ها را در این لیست وارد کن

bot = telebot.TeleBot(TOKEN)

# فایل ذخیره‌سازی اطلاعات کاربران
USER_DATA_FILE = 'users_data.json'

# دیکشنری برای پیگیری مراحل ثبت‌نام کاربران
user_states = {}  # key: chat_id, value: مرحله ثبت‌نام
user_data = {}  # ذخیره اطلاعات کاربران موقتاً تا پایان ثبت‌نام

# بارگذاری اطلاعات کاربران از فایل JSON
def load_users():
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
            if isinstance(users_data, list):
                return users_data
            else:
                return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # اگر فایل وجود نداشت یا خراب بود، لیست خالی برمی‌گردانیم

# ذخیره اطلاعات کاربران در فایل JSON
def save_users():
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# مقداردهی لیست کاربران هنگام اجرای برنامه
users = load_users()



# آیدی گروه
GROUP_CHAT_ID = '-1002120912138'  # آیدی گروه را اینجا قرار دهید

bot = telebot.TeleBot(TOKEN)

# پیام‌هایی که قرار است ارسال شوند
messages = [
    "🌟 *لینک حمایت* 🌟\n\n"
    "برای حمایت از ماریا و بزرگترین برزگران کننده دویل های کالاف موبایل، کافی‌ست روی لینک زیر کلیک کنید و با محبت خود ماریا را همراهی کنید!\n\n"
    "🔗 *لینک حمایت:* [https://reymit.ir/mariyarxo]\n\n(https://reymit.ir/mariyarxo)\n\n"
    "با حمایت شما، استریم‌های بهتر و جذاب‌تری خواهیم داشت! ❤️",
    "🎮 *استریم‌های هیجان‌انگیز ماریا هر هفته!* 🌟\n\n 
    
    📅 روزهای *شنبه* - *دوشنبه* - *چهارشنبه* هر هفته
    ⏰ *ساعت ۹ شب* به وقت ایران.",
    "📺 لینک کانال یوتیوب ماریا   /n/n  : https://www.youtube.com/@MariyaRxo"
]

# تابع ارسال پیام
def send_automatic_messages():
    if messages:
        message_text = messages.pop(0)  # برداشتن اولین پیام از لیست
        try:
            bot.send_message(GROUP_CHAT_ID, message_text)
            print(f"پیام ارسال شد: {message_text}")  # برای بررسی
        except Exception as e:
            print(f"خطا در ارسال پیام به گروه: {e}")
    else:
        print("تمام پیام‌ها ارسال شدند.")

# زمان‌بندی پیام‌ها برای ارسال هر 1 دقیقه یک‌بار
def schedule_messages():
    schedule.every(1).minutes.do(send_automatic_messages)  # ارسال هر 1 دقیقه
    print("زمان‌بندی شروع شده است.")
    while True:
        schedule.run_pending()
        time.sleep(1)

# اجرای تابع زمان‌بندی در یک رشته جداگانه
threading.Thread(target=schedule_messages, daemon=True).start()



# شروع ثبت‌نام
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    if chat_id in user_states:  # اگر کاربر قبلاً استارت زده
        bot.send_message(chat_id, "❌ شما در حال حاضر در فرآیند ثبت‌نام هستید. لطفاً اطلاعات خواسته‌شده را وارد کنید.")
        return
    
    if any(user['chat_id'] == chat_id for user in users):
        bot.send_message(chat_id, "❌ شما قبلاً اطلاعات خود را ثبت کرده‌اید.")
        return

    user_states[chat_id] = "name"  # تنظیم مرحله به "نام"
    user_data[chat_id] = {}  # ایجاد یک دیکشنری برای ذخیره اطلاعات کاربر
    bot.send_message(chat_id, "سلام برای ثبت اطلاعات روی هر پیام ریپلای بزنید! لطفاً نام و نام خانوادگی خود را وارد کنید:")

# دریافت نام و رفتن به مرحله بعد
@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id] == "name")
def process_name(message):
    chat_id = message.chat.id
    user_data[chat_id]["name"] = message.text  # ذخیره نام
    user_states[chat_id] = "cod_id"  # تغییر مرحله به دریافت آیدی کالاف
    bot.send_message(chat_id, "حالا لطفاً آیدی کالاف موبایل خود را وارد کنید:")

# دریافت آیدی کالاف و رفتن به مرحله بعد
@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id] == "cod_id")
def process_cod_id(message):
    chat_id = message.chat.id
    user_data[chat_id]["cod_id"] = message.text  # ذخیره آیدی کالاف
    user_states[chat_id] = "cod_name"  # تغییر مرحله به دریافت نام اکانت
    bot.send_message(chat_id, "نام اکانت کالاف موبایل خود را وارد کنید:")

# دریافت نام اکانت و رفتن به مرحله بعد
@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id] == "cod_name")
def process_cod_name(message):
    chat_id = message.chat.id
    user_data[chat_id]["cod_name"] = message.text  # ذخیره نام اکانت
    user_states[chat_id] = "level"  # تغییر مرحله به دریافت لول اکانت
    bot.send_message(chat_id, "لول اکانت کالاف خود را وارد کنید:")

# دریافت لول اکانت و اتمام ثبت‌نام
@bot.message_handler(func=lambda message: message.chat.id in user_states and user_states[message.chat.id] == "level")
def process_level(message):
    chat_id = message.chat.id
    user_data[chat_id]["level"] = message.text  # ذخیره لول

    # اضافه کردن کاربر به لیست و ذخیره در فایل JSON
    users.append({
        'chat_id': chat_id,
        'name': user_data[chat_id]['name'],
        'cod_id': user_data[chat_id]['cod_id'],
        'cod_name': user_data[chat_id]['cod_name'],
        'level': user_data[chat_id]['level'],
        'submitted': True
    })
    save_users()

    # ارسال اطلاعات نهایی
    info_text = (f"✅ اطلاعات شما ثبت شد:\n"
                 f"👤 نام: {user_data[chat_id]['name']}\n"
                 f"🎮 آیدی کالاف: {user_data[chat_id]['cod_id']}\n"
                 f"🆔 نام اکانت: {user_data[chat_id]['cod_name']}\n"
                 f"⭐ لول: {user_data[chat_id]['level']}")

    bot.send_message(chat_id, info_text)

    # ارسال اطلاعات به ادمین‌ها
    for admin in ADMIN_USERS:
        bot.send_message(admin, "📥 ثبت‌نام جدید:\n" + info_text)

    # پاک کردن وضعیت کاربر بعد از اتمام ثبت‌نام
    del user_states[chat_id]
    del user_data[chat_id]

# نمایش اطلاعات ثبت شده برای ادمین
@bot.message_handler(commands=['namyesh'])
def show_user_info_for_all(message):
    users = load_users()  # خواندن داده‌های کاربران

    all_info = ""
    for user in users:
        if user.get('submitted', False):
            info_text = (f"👤 نام: {user['name']}\n"
                         f"🎮 آیدی کالاف: {user['cod_id']}\n"
                         f"🆔 نام اکانت: {user['cod_name']}\n"
                         f"⭐ لول: {user['level']}\n"
                         "------------------------\n")
            all_info += info_text

    if all_info:
        bot.send_message(message.chat.id, f"📋 لیست کاربران ثبت‌شده:\n\n{all_info}")  
    else:
        bot.send_message(message.chat.id, "❌ هیچ اطلاعاتی ثبت نشده است.")

# پاک کردن اطلاعات کاربران (فقط ادمین‌ها)
@bot.message_handler(commands=['refresh'])
def refresh_users(message):
    if message.chat.id in ADMIN_USERS:
        global users
        users = []
        save_users()
        bot.send_message(message.chat.id, "✅ تمام اطلاعات کاربران پاک شد.")
    else:
        bot.send_message(message.chat.id, "❌ شما ادمین نیستید و دسترسی به این دستور ندارید.")

# اجرای ربات
bot.polling(none_stop=True)
