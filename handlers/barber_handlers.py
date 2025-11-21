from telebot.types import Message
from database.service import DatabaseService
from utils.keyboards import get_main_menu
from utils.helpers import format_date
from config import ADMIN_IDS


def setup_barber_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == "🧺 Mening sochiqlarim")
    def my_towels_handler(message: Message):
        user_id = message.from_user.id
        
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(user_id)

            if not user:
                bot.send_message(message.chat.id, "Siz ro'yxatdan o'tmagansiz!")
                return

            towel_count = user.get('towel_count', 0)
            updated_at = format_date(user.get('updated_at', ''))

            response_text = (
                f"🧺 Sizning sochiqlaringiz\n\n"
                f"🔢 Sochiqlar soni: {towel_count} ta\n\n"
                f"Yangilanish: {updated_at}"
            )

            bot.send_message(message.chat.id, response_text)

    @bot.message_handler(func=lambda message: message.text == "📋 Mening tarixim")
    def my_history_handler(message: Message):
        user_id = message.from_user.id
        
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(user_id)

            if not user:
                bot.send_message(message.chat.id, "Siz ro'yxatdan o'tmagansiz!")
                return

            transactions = db_service.get_user_transactions(user['id'])

            if not transactions:
                bot.send_message(message.chat.id, "Hozircha hech qanday operatsiya yo'q.")
                return

            history_text = "📋 Operatsiyalar tarixi\n\n"

            for i, transaction in enumerate(transactions[:10], 1):
                type_emoji = "✅" if transaction.get('transaction_type') == 'given' else "❌"
                type_text = "Olindi" if transaction.get('transaction_type') == 'given' else "Berildi"
                quantity = transaction.get('quantity', 0)

                # Vaqtni formatlash
                date = format_date(transaction.get('created_at', ''))

                history_text += f"{i}. {type_emoji} {type_text}: {quantity} ta\n"
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
