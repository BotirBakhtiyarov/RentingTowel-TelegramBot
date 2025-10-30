from telebot.types import Message
from utils.api_client import api_client
from utils.keyboards import get_main_menu
from utils.helpers import format_date, format_date_only
from config import ADMIN_IDS


def setup_barber_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "🧺 Mening sochiqlarim")
    def my_towels_handler(message: Message):
        user_id = message.from_user.id
        barber = api_client.get_barber_by_telegram_id(user_id)

        if not barber:
            bot.send_message(message.chat.id, "Siz ro'yxatdan o'tmagansiz!")
            return

        towel_count = barber.get('towel_count', 0)

        # towel_price ni to'g'ri formatda olish
        towel_price = barber.get('towel_price', 0)
        try:
            if isinstance(towel_price, str):
                towel_price = float(towel_price)
        except (ValueError, TypeError):
            towel_price = 0

        # Jami qiymatni to'g'ri hisoblash
        total_value = towel_count * towel_price

        # Vaqtni formatlash
        updated_at = format_date(barber.get('updated_at', ''))

        response_text = (
            f"🧺 Sizning sochiqlaringiz\n\n"
            f"🔢 Sochiqlar soni: {towel_count} ta\n"
            f"💰 Sochiq narxi: {towel_price:,.0f} so'm\n"
            f"💵 Jami qiymat: {total_value:,.0f} so'm\n\n"
            f"Yangilash: {updated_at}"
        )

        bot.send_message(message.chat.id, response_text)

    @bot.message_handler(func=lambda message: message.text == "📋 Mening tarixim")
    def my_history_handler(message: Message):
        user_id = message.from_user.id
        barber = api_client.get_barber_by_telegram_id(user_id)

        if not barber:
            bot.send_message(message.chat.id, "Siz ro'yxatdan o'tmagansiz!")
            return

        transactions = api_client.get_barber_transactions(barber['id'])

        if not transactions:
            bot.send_message(message.chat.id, "Hozircha hech qanday operatsiya yo'q.")
            return

        history_text = "📋 Operatsiyalar tarixi\n\n"

        for i, transaction in enumerate(transactions[:10], 1):
            type_emoji = "✅" if transaction.get('transaction_type') == 'given' else "❌"
            type_text = "Olindi" if transaction.get('transaction_type') == 'given' else "Berildi"
            quantity = transaction.get('quantity', 0)

            # total_price ni to'g'ri formatda olish
            total_price = transaction.get('total_price', 0)
            try:
                if isinstance(total_price, str):
                    total_price = float(total_price)
            except (ValueError, TypeError):
                total_price = 0

            # Vaqtni formatlash
            date = format_date(transaction.get('created_at', ''))

            history_text += f"{i}. {type_emoji} {type_text}: {quantity} ta\n"
            if total_price > 0:
                history_text += f"   💰 {total_price:,.0f} so'm\n"
            history_text += f"   📅 {date}\n\n"

        bot.send_message(message.chat.id, history_text)

    @bot.message_handler(func=lambda message: message.text == "🔙 Asosiy menu")
    def back_to_main_handler(message: Message):
        user_id = message.from_user.id
        is_admin = user_id in ADMIN_IDS
        bot.send_message(
            message.chat.id,
            "Asosiy menu:",
            reply_markup=get_main_menu(user_id, is_admin)
        )