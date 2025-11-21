import requests
import socks
import socket
from config import BOT_TOKEN

# Proxy sozlamalari
SOCKS_PROXY_HOST = '127.0.0.1'
SOCKS_PROXY_PORT = 10808


def set_socks_proxy():
    # SOCKS proxy ni global socket ga o'rnatish
    socks.set_default_proxy(socks.SOCKS5, SOCKS_PROXY_HOST, SOCKS_PROXY_PORT)
    socket.socket = socks.socksocket


def test_proxy_connection():
    print("=== Proxy Test Dasturi ===")
    print(f"Proxy: {SOCKS_PROXY_HOST}:{SOCKS_PROXY_PORT}")

    # Avval proxy ni o'rnatamiz
    set_socks_proxy()

    # 1. Umumiy internet aloqasini tekshirish
    print("\n1. Umumiy internet aloqasini tekshirish...")
    try:
        response = requests.get('https://httpbin.org/ip', timeout=10)
        print(f"✅ Proxy orqali internetga ulandi")
        print(f"   IP manzil: {response.json()['origin']}")
    except Exception as e:
        print(f"❌ Proxy orqali internetga ulanib bo'lmadi: {e}")
        return False

    # 2. Telegram API ga ulanishni tekshirish
    print("\n2. Telegram API ga ulanishni tekshirish...")
    try:
        response = requests.get('https://api.telegram.org', timeout=10)
        print("✅ Telegram API ga proxy orqali ulandi")
    except Exception as e:
        print(f"❌ Telegram API ga ulanib bo'lmadi: {e}")
        return False

    # 3. Bot tokenini tekshirish
    print("\n3. Bot tokenini tekshirish...")
    try:
        from telebot import apihelper
        # apihelper ni proxy sozlamalari bilan sozlash
        apihelper.proxy = {'https': f'socks5://{SOCKS_PROXY_HOST}:{SOCKS_PROXY_PORT}'}
        import telebot
        bot = telebot.TeleBot(BOT_TOKEN)
        bot_info = bot.get_me()
        print(f"✅ Bot muvaffaqiyatli ulandi: @{bot_info.username}")
        return True
    except Exception as e:
        print(f"❌ Bot tokeni noto'g'ri yoki ulanib bo'lmadi: {e}")
        return False


if __name__ == '__main__':
    if test_proxy_connection():
        print("\n🎉 Barcha testlar muvaffaqiyatli! Botni ishga tushirishingiz mumkin.")
    else:
        print("\n⚠️  Proxy sozlamalarida muammo bor. Quyidagilarni tekshiring:")
        print("   - SOCKS5 proxy server ishlamayapti (127.0.0.1:10808)")
        print("   - Proxy dasturi (masalan, Shadowsocks, V2Ray) ishlamayapti")
        print("   - Port noto'g'ri sozlangan")