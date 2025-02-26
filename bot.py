import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'  # توکن ربات خود را جایگزین کنید

# لیست آیدی‌های ادمین‌ها (چندین ادمین می‌تونن باشن)
ADMIN_USERS = [1891217517 , 6442428304]  # آیدی‌های ادمین‌ها را در این لیست وارد کن

bot = telebot.TeleBot(TOKEN)

# فایل ذخیره‌سازی اطلاعات کاربران
USER_DATA_FILE = 'users_data.json'

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

# پرچم برای کنترل اینکه آیا اطلاعات پاک شده‌اند یا خیر
refresh_flag = False

# شروع ربات و خوشامدگویی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global users  # تا بتوانیم مقدار را ذخیره کنیم
    chat_id = message.chat.id

    # بررسی اینکه آیا کاربر قبلاً ثبت شده یا نه
    if not any(user['chat_id'] == chat_id for user in users):
        users.append({'chat_id': chat_id, 'name': '', 'cod_id': '', 'cod_name': '', 'level': '', 'submitted': False})
        save_users()
        bot.send_message(chat_id, "سلام! لطفاً اطلاعات زیر را وارد کنید.")
        request_name(message)
    else:
        bot.send_message(chat_id, "❌شما قبلاً اطلاعات خود را ثبت کرده‌اید.")

# درخواست نام و نام خانوادگی
def request_name(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "نام و نام خانوادگی خود را وارد کنید:")
    bot.register_next_step_handler(msg, process_name)

# پردازش نام و نام خانوادگی
def process_name(message):
    global users
    chat_id = message.chat.id
    for user in users:
        if user['chat_id'] == chat_id:
            user['name'] = message.text
            break
    save_users()
    msg = bot.send_message(chat_id, "آیدی کالاف موبایل خود را وارد کنید:")
    bot.register_next_step_handler(msg, process_cod_id)

# پردازش آیدی کالاف
def process_cod_id(message):
    global users
    chat_id = message.chat.id
    for user in users:
        if user['chat_id'] == chat_id:
            user['cod_id'] = message.text
            break
    save_users()
    msg = bot.send_message(chat_id, "نام اکانت کالاف موبایل خود را وارد کنید:")
    bot.register_next_step_handler(msg, process_cod_name)

# پردازش نام اکانت کالاف
def process_cod_name(message):
    global users
    chat_id = message.chat.id
    for user in users:
        if user['chat_id'] == chat_id:
            user['cod_name'] = message.text
            break
    save_users()
    msg = bot.send_message(chat_id, "لول اکانت کالاف خود را وارد کنید:")
    bot.register_next_step_handler(msg, process_level)

# پردازش لول اکانت کالاف
def process_level(message):
    global users
    chat_id = message.chat.id
    for user in users:
        if user['chat_id'] == chat_id:
            user['level'] = message.text
            break
    save_users()
    
    # دکمه ثبت اطلاعات
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ ثبت اطلاعات", callback_data='submit_info'))
    
    bot.send_message(chat_id, "همه اطلاعات دریافت شد. لطفاً دکمه زیر را برای ثبت بزنید.", reply_markup=markup)

# پردازش کلیک روی دکمه ثبت اطلاعات
@bot.callback_query_handler(func=lambda call: call.data == 'submit_info')
def send_info_to_admin(call):
    global users
    chat_id = call.message.chat.id
    user_info = next((user for user in users if user['chat_id'] == chat_id), None)
    
    if user_info:
        if user_info['submitted']:
            bot.send_message(chat_id, "❌ شما قبلاً اطلاعات خود را ثبت کرده‌اید.")
            return
        
        user_info['submitted'] = True
        save_users()
        
        info_text = (f"اطلاعات جدید ثبت شد:\n"
                     f"👤 نام: {user_info['name']}\n"   
                     f"🎮 آیدی کالاف: {user_info['cod_id']}\n"
                     f"🆔 نام اکانت: {user_info['cod_name']}\n"
                     f"⭐ لول: {user_info['level']}")
        
        for admin in ADMIN_USERS:
            bot.send_message(admin, info_text)  # ارسال اطلاعات به تمامی ادمین‌ها
        
        bot.send_message(chat_id, "✅ اطلاعات شما با موفقیت ثبت شد!")

    else:
        bot.send_message(chat_id, "❌ خطا در ثبت اطلاعات. لطفاً دوباره تلاش کنید.")

# دریافت Chat ID کاربر
@bot.message_handler(commands=['myid'])
def send_my_id(message):
    bot.send_message(message.chat.id, f"Your Chat ID: {message.chat.id}")

# نمایش اطلاعات ثبت شده برای ادمین
@bot.message_handler(commands=['namyesh'])
def show_user_info(message):
    global users  
    users = load_users()  # اطمینان از خواندن داده‌ها

    all_info = ""
    for user in users:
        if user.get('submitted', False):
            info_text = (f"اطلاعات کاربر:\n"
                         f"👤 نام: {user['name']}\n"   
                         f"🎮 آیدی کالاف: {user['cod_id']}\n"
                         f"🆔 نام اکانت: {user['cod_name']}\n"
                         f"⭐ لول: {user['level']}\n\n"
                         "------------------------\n")
            all_info += info_text
    
    if all_info:
        bot.send_message(message.chat.id, all_info)  # نمایش اطلاعات برای همه کاربران
    else:
        bot.send_message(message.chat.id, "❌ هیچ اطلاعاتی ثبت نشده است.")
        
# پاک کردن اطلاعات کاربران
@bot.message_handler(commands=['refresh'])
def refresh_users(message):
    global users
    if message.chat.id in ADMIN_USERS:  # بررسی اگر کاربر یکی از ادمین‌ها باشد
        users = []  # لیست کاربران را خالی می‌کند
        save_users()
        bot.send_message(message.chat.id, "تمام اطلاعات کاربران پاک شد.")
    else:
        bot.send_message(message.chat.id, "❌ شما ادمین نیستید و دسترسی به این دستور ندارید.")

# اجرای ربات
bot.polling(none_stop=True)
