import telebot
from telebot import apihelper
from config import BOT_TOKEN

# SOCKS5 proxy sozlamalari (Firefoxdagiga o'xshash)
SOCKS_PROXY = 'socks5://127.0.0.1:10808'

# Proxy ni o'rnatish
apihelper.proxy = {'https': SOCKS_PROXY}

# Handlerlarni import qilish
from handlers.register_handlers import setup_register_handlers
from handlers.barber_handlers import setup_barber_handlers
from handlers.admin_handlers import setup_admin_handlers


def main():
    try:
        # Botni yaratish
        bot = telebot.TeleBot(BOT_TOKEN)

        # Handlerlarni sozlash
        setup_register_handlers(bot)
        setup_barber_handlers(bot)
        setup_admin_handlers(bot)

        print("Bot proxy orqali ishga tushdi...")
        print(f"Proxy: {SOCKS_PROXY}")

        # Botni ishga tushirish
        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except Exception as e:
        print(f"Xato yuz berdi: {e}")
        print("Proxy sozlamalari noto'g'ri bo'lishi mumkin")


if __name__ == '__main__':
    main()