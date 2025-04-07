import telebot
import schedule
import time
import threading

# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'

# آیدی گروه
GROUP_CHAT_ID = '-1002120912138'  # آیدی گروه را اینجا قرار دهید

bot = telebot.TeleBot(TOKEN)

# پیام‌هایی که قرار است ارسال شوند
messages = [
    "🌟 *حمایت از ما به راحتی!* 🌟\n\n"
    "برای حمایت از ماریا و استریم‌های شگفت‌انگیز او، کافی‌ست روی لینک زیر کلیک کنید و با محبت خود ماریا را همراهی کنید!\n\n"
    "🔗 *لینک حمایت:* [https://reymit.ir/mariyarxo](https://reymit.ir/mariyarxo)\n\n"
    "با حمایت شما، استریم‌های بهتر و جذاب‌تری خواهیم داشت! ❤️",
    "🎮 روزهای شنبه - دوشنبه - چهارشنبه استریم از کانال یوتیوب ساعت ۹ شب",
    "📺 لینک کانال یوتیوب ماریا: https://www.youtube.com/@MariyaRxo"
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

# اجرای ربات
bot.polling(none_stop=True)
