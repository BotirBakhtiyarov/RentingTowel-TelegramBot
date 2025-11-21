import telebot
from telebot import apihelper
from config import BOT_TOKEN, PROXY_ENABLED, PROXY_URL
from database.db import init_db

# Proxy sozlamalari (ixtiyoriy)
if PROXY_ENABLED:
    apihelper.proxy = {'https': PROXY_URL}

# Handlerlarni import qilish
from handlers.register_handlers import setup_register_handlers
from handlers.barber_handlers import setup_barber_handlers
from handlers.admin_handlers import setup_admin_handlers


def main():
    try:
        # Database ni ishga tushirish
        print("Database ni ishga tushiryapman...")
        init_db()
        print("Database muvaffaqiyatli yaratildi/yuklandi!")

        # Botni yaratish
        bot = telebot.TeleBot(BOT_TOKEN)

        # Handlerlarni sozlash
        setup_register_handlers(bot)
        setup_barber_handlers(bot)
        setup_admin_handlers(bot)

        if PROXY_ENABLED:
            print(f"Bot proxy orqali ishga tushdi...")
            print(f"Proxy: {PROXY_URL}")
        else:
            print("Bot ishga tushdi (proxy o'chirilgan)")

        # Botni ishga tushirish
        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception as e:
        print(f"Xato yuz berdi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
