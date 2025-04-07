import telebot

# تنظیم Token ربات
TOKEN = '7937158820:AAG_GEmXp5KeooUoIp3X_S9dIucEBXcoHT8'

bot = telebot.TeleBot(TOKEN)

# متد برای دریافت اطلاعات آخرین پیام‌ها
@bot.message_handler(func=lambda message: True)
def get_group_id(message):
    print("Group Chat ID:", message.chat.id)  # این خط آیدی گروه را در لاگ چاپ می‌کند
    bot.reply_to(message, f"آیدی گروه: {message.chat.id}")

# اجرای ربات
bot.polling(none_stop=True)
