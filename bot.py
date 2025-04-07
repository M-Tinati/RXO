import telebot
import schedule
import time
import threading

# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'

# آیدی گروه
GROUP_CHAT_ID = '-1002120912138'  # آیدی گروه را اینجا قرار دهید

bot = telebot.TeleBot(TOKEN)

def send_automatic_messages():
    message_text = (
        "🔔 لینک حمایت: https://reymit.ir/mariyarxo\n\n"
        "🎮 روزهای شنبه - دوشنبه - چهارشنبه استریم از کانال یوتیوب ساعت ۹ شب\n\n"
        "📺 لینک کانال یوتیوب ماریا: https://www.youtube.com/@MariyaRxo"
    )

    try:
        bot.send_message(GROUP_CHAT_ID, message_text)
        print("پیام به گروه ارسال شد.")  # برای بررسی
    except Exception as e:
        print(f"خطا در ارسال پیام به گروه: {e}")

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
