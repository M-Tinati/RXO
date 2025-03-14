import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json


# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'

# لیست آیدی‌های ادمین‌ها
ADMIN_USERS = [1891217517,6442428304,6982477095]  # آیدی‌های ادمین‌ها را در این لیست وارد کن

bot = telebot.TeleBot(TOKEN)

# فایل ذخیره‌سازی اطلاعات کاربران
USER_DATA_FILE = 'users_data.json'

# دیکشنری برای پیگیری مراحل ثبت‌نام کاربران
user_states = {}  # key: chat_id, value: مرحله ثبت‌نام
user_data = {}  # ذخیره اطلاعات کاربران موقتاً تا پایان ثبت‌نام

# دیکشنری جدید برای پیگیری مراحل خرید CP
purchase_states = {}  # key: chat_id, value: مرحله خرید
purchase_data = {}  # ذخیره اطلاعات خرید کاربران موقتاً

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

# دکمه‌های شیشه‌ای برای خرید CP
@bot.message_handler(commands=['kharid_cp'])
def buy_cp(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    # دکمه‌ها برای انتخاب خرید
    markup.add(InlineKeyboardButton("50 CP - 100,000 تومان", callback_data="buy_50"))
    markup.add(InlineKeyboardButton("60 CP - 100,000 تومان", callback_data="buy_60"))
    markup.add(InlineKeyboardButton("70 CP - 100,000 تومان", callback_data="buy_70"))
    markup.add(InlineKeyboardButton("100 CP - 100,000 تومان", callback_data="buy_100"))
    markup.add(InlineKeyboardButton("240 CP - 100,000 تومان", callback_data="buy_240"))
    markup.add(InlineKeyboardButton("320 CP - 100,000 تومان", callback_data="buy_320"))
    markup.add(InlineKeyboardButton("500 CP - 100,000 تومان", callback_data="buy_500"))
    markup.add(InlineKeyboardButton("1080 CP - 100,000 تومان", callback_data="buy_1080"))
    bot.send_message(chat_id, "لطفاً تعداد CP را انتخاب کنید:", reply_markup=markup)

# مدیریت انتخاب CP و مراحل بعدی
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy_cp(call):
    chat_id = call.message.chat.id
    cp_amount = call.data.split('_')[1]  # استخراج تعداد CP
    purchase_states[chat_id] = "name"  # شروع پروسه ثبت خرید

    # ذخیره تعداد CP خریداری شده موقتاً
    purchase_data[chat_id] = {'cp_amount': cp_amount}
    
    bot.send_message(chat_id, f"شما {cp_amount} CP خریداری کرده‌اید.\nلطفاً نام و نام خانوادگی خود را وارد کنید:")

# دریافت نام و اطلاعات جیمیل و رمز
@bot.message_handler(func=lambda message: message.chat.id in purchase_states and purchase_states[message.chat.id] == "name")
def process_name_for_purchase(message):
    chat_id = message.chat.id
    purchase_data[chat_id]["name"] = message.text  # ذخیره نام
    purchase_states[chat_id] = "email"  # تغییر مرحله به دریافت جیمیل
    bot.send_message(chat_id, "لطفاً جیمیل خود را وارد کنید:")

# دریافت جیمیل و رمز جیمیل
@bot.message_handler(func=lambda message: message.chat.id in purchase_states and purchase_states[message.chat.id] == "email")
def process_email_for_purchase(message):
    chat_id = message.chat.id
    purchase_data[chat_id]["email"] = message.text  # ذخیره جیمیل
    purchase_states[chat_id] = "password"  # تغییر مرحله به دریافت رمز
    bot.send_message(chat_id, "لطفاً رمز جیمیل خود را وارد کنید:")

# دریافت رمز جیمیل
@bot.message_handler(func=lambda message: message.chat.id in purchase_states and purchase_states[message.chat.id] == "password")
def process_password_for_purchase(message):
    chat_id = message.chat.id
    purchase_data[chat_id]["password"] = message.text  # ذخیره رمز جیمیل
    purchase_states[chat_id] = "card_info"  # تغییر مرحله به نمایش شماره کارت
    # نمایش شماره کارت برای واریز
    bot.send_message(chat_id, "لطفاً وجه مورد نظر را به شماره کارت زیر واریز کنید:\n\n"
                              "📝 شماره کارت: 0000-000-0000-0000\n\n"
                              "بعد از واریز، تصویر واریز رابه ایدی ادمین @Rxobotadmin ارسال کنید.((ارسال عکس اختیاری میباشد اگر عکس نگرفتید یک عکس خالی بفرستید یا عکس کالافتونو بفرستید)")


# دریافت عکس واریزی (اختیاری)
@bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id in purchase_states and purchase_states[message.chat.id] == "card_info")
def process_receipt_image(message):
    chat_id = message.chat.id
    purchase_data[chat_id]["receipt_image"] = message.photo[-1].file_id  # ذخیره عکس واریزی
    purchase_states[chat_id] = "final_step"  # تغییر مرحله به نهایی
    bot.send_message(
        chat_id,
        "تمام شد! برای ثبت نهایی اطلاعات بر روی دکمه زیر کلیک کنید.",
        reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("ثبت اطلاعات", callback_data="final_submit"))
    )

# اضافه کردن دکمه "بعدی" در صورتی که کاربر عکس ارسال نکرد
@bot.message_handler(func=lambda message: message.chat.id in purchase_states and purchase_states[message.chat.id] == "card_info")
def handle_no_receipt_image(message):
    chat_id = message.chat.id
    if 'photo' not in message:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("بعدی", callback_data="next_step"))  # دکمه بعدی

        bot.send_message(
            chat_id,
            "شما عکسی ارسال نکردید. اگر مایلید به مرحله بعدی بروید، بر روی دکمه 'بعدی' کلیک کنید.",
            reply_markup=markup
        )

# مدیریت دکمه "بعدی" و رفتن به مرحله بعد
@bot.callback_query_handler(func=lambda call: call.data == "next_step")
def next_step(call):
    chat_id = call.message.chat.id
    purchase_states[chat_id] = "final_step"  # تغییر مرحله به نهایی
    bot.send_message(
        chat_id,
        "شما به مرحله بعدی رفته‌اید! برای ثبت نهایی اطلاعات بر روی دکمه زیر کلیک کنید.",
        reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("ثبت اطلاعات", callback_data="final_submit"))
    )

# ثبت اطلاعات نهایی و ذخیره در فایل
@bot.callback_query_handler(func=lambda call: call.data == "final_submit")
def submit_purchase_info(call):
    chat_id = call.message.chat.id
    if chat_id in purchase_data:
        # ذخیره اطلاعات در فایل JSON
        user_purchase_info = {
            'chat_id': chat_id,
            'cp_amount': purchase_data[chat_id]['cp_amount'],
            'name': purchase_data[chat_id]['name'],
            'email': purchase_data[chat_id]['email'],
            'password': purchase_data[chat_id]['password'],
            'receipt_image': purchase_data[chat_id].get('receipt_image', None)
        }
        with open('purchases_data.json', 'a', encoding='utf-8') as f:
            json.dump(user_purchase_info, f, ensure_ascii=False, indent=4)
            f.write("\n")  # یک خط جدید برای هر خرید
        bot.send_message(chat_id, "✅  اطلاعات شما ثبت شد تا 24 ساعت آینده واریز میشه!")
        # پاک کردن اطلاعات کاربر
        del purchase_states[chat_id]
        del purchase_data[chat_id]
# دستور برای مشاهده خریدها (فقط برای ادمین‌ها)
@bot.message_handler(commands=['moshahede_kharidar'])
def view_purchases(message):
    if message.chat.id in ADMIN_USERS:
        try:
            with open('purchases_data.json', 'r', encoding='utf-8') as f:
                purchases = f.readlines()
                if purchases:
                    all_purchases = "".join(purchases)
                    bot.send_message(message.chat.id, f"📋 لیست خریدهای ثبت‌شده:\n\n{all_purchases}")
                else:
                    bot.send_message(message.chat.id, "❌ هیچ خریدی ثبت نشده است.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "❌ فایل خریدها پیدا نشد.")
    else:
        bot.send_message(message.chat.id, "❌ شما ادمین نیستید و دسترسی به این دستور ندارید.")






















ADMIN_GEM = [1891217517]  # آیدی تلگرام ادمین‌ها


# موقعیت الماس‌ها (پیش‌فرض)
gem_positions = [(0, 0), (1, 2), (2, 1)]
user_progress = {}  # ذخیره‌ی الماس‌های پیدا شده‌ی هر کاربر
user_lost = {}  # ذخیره‌ی وضعیت باخت کاربران

def create_game_board(chat_id, reveal_gems=False):
    markup = InlineKeyboardMarkup(row_width=3)
    for i in range(3):
        buttons = []
        for j in range(3):
            if reveal_gems and (i, j) in gem_positions:
                btn_text = '💎'  # نمایش الماس بعد از باخت
            elif chat_id in user_progress and (i, j) in user_progress[chat_id]:
                btn_text = '💎'  # الماس پیدا شده
            else:
                btn_text = '❓'  # هنوز کشف نشده
            buttons.append(InlineKeyboardButton(btn_text, callback_data=f'box_{i}_{j}'))
        markup.add(*buttons)
    return markup

@bot.message_handler(commands=['game'])
def start_game(message):
    chat_id = message.chat.id
    if chat_id in user_lost and user_lost[chat_id]:
        bot.send_message(chat_id, "❌ شما باخته‌اید! لطفاً منتظر تنظیم مجدد بازی باشید.")
        return
    if chat_id in user_progress and len(user_progress[chat_id]) >= 3:
        bot.send_message(chat_id, "✅ شما قبلاً هر ۳ الماس را پیدا کرده‌اید! منتظر تنظیم مجدد بازی باشید.")
        return
    
    user_progress[chat_id] = []  # لیست خالی برای کاربر جدید
    bot.send_message(chat_id, "🎮 بازی شروع شد! یکی از باکس‌ها را انتخاب کنید:", reply_markup=create_game_board(chat_id))

@bot.callback_query_handler(func=lambda call: call.data.startswith('box_'))
def box_clicked(call):
    chat_id = call.message.chat.id
    _, i, j = call.data.split('_')
    i, j = int(i), int(j)
    
    if chat_id in user_lost and user_lost[chat_id]:
        bot.answer_callback_query(call.id, "❌ شما قبلاً باخته‌اید!")
        return
    
    if chat_id not in user_progress:
        user_progress[chat_id] = []
    
    if (i, j) in user_progress[chat_id]:
        bot.answer_callback_query(call.id, "⛔ این الماس را قبلاً پیدا کرده‌اید!")
        return
    
    if (i, j) in gem_positions:
        user_progress[chat_id].append((i, j))
        bot.edit_message_text("🎉 شما یک الماس پیدا کردید! ادامه دهید...", chat_id, call.message.message_id, reply_markup=create_game_board(chat_id))
        
        if len(user_progress[chat_id]) == 3:
            bot.send_message(chat_id, "🎉🎉 تبریک! شما هر ۳ الماس را پیدا کردید! 💎🏆")
    else:
        user_lost[chat_id] = True  # ثبت وضعیت باخت
        bot.send_message(chat_id, "❌ متاسفم، شما باختید! این هم مکان الماس‌ها:", reply_markup=create_game_board(chat_id, True))

@bot.message_handler(commands=['resetgem'])
def reset_game(message):
    if message.chat.id not in ADMIN_GEM:
        bot.send_message(message.chat.id, "❌ شما ادمین نیستید!")
        return
    global user_progress, user_lost
    user_progress = {}
    user_lost = {}
    bot.send_message(message.chat.id, "✅ بازی برای همه کاربران بازنشانی شد!")

@bot.message_handler(commands=['setgems'])
def set_gems(message):
    if message.chat.id not in ADMIN_GEM:
        bot.send_message(message.chat.id, "❌ شما ادمین نیستید!")
        return
    bot.send_message(message.chat.id, "لطفاً موقعیت جدید الماس‌ها را با فرمت x,y;x,y;x,y ارسال کنید.")

@bot.message_handler(func=lambda message: message.chat.id in ADMIN_GEM and ',' in message.text)
def update_gems(message):
    global gem_positions
    try:
        new_positions = [tuple(map(int, pos.split(','))) for pos in message.text.split(';')]
        if all(0 <= x < 3 and 0 <= y < 3 for x, y in new_positions):
            gem_positions = new_positions
            bot.send_message(message.chat.id, "✅ موقعیت الماس‌ها به‌روزرسانی شد!")
        else:
            bot.send_message(message.chat.id, "❌ مختصات نامعتبر است! فقط عددهای بین 0 و 2 مجاز هستند.")
    except:
        bot.send_message(message.chat.id, "❌ فرمت نامعتبر! لطفاً به‌درستی وارد کنید.")









# اجرای ربات
bot.polling(none_stop=True)
