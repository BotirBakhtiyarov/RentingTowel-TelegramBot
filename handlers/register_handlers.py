from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from database.service import DatabaseService
from utils.keyboards import get_main_menu, get_register_keyboard
from utils.helpers import format_date
from config import ADMIN_IDS

# Ro'yxatdan o'tish jarayonini kuzatish uchun
user_registration_data = {}


def setup_register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start_handler(message: Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        # Foydalanuvchini tekshirish
        with DatabaseService() as db_service:
            user = db_service.get_user_by_telegram_id(user_id)
            is_admin = user_id in ADMIN_IDS

            if user or is_admin:
                # Agar ro'yxatdan o'tgan bo'lsa
                welcome_text = f"Assalomu alaykum {user_name}!\n"
                if is_admin:
                    welcome_text += "Siz admin sifatida kirdingiz. 🛠️"
                else:
                    # Vaqtni formatlash
                    updated_at = format_date(user.get('updated_at', ''))
                    welcome_text += f"Foydalanuvchi sifatida kirdingiz. 🧑‍💼\nSochiqlar soni: {user.get('towel_count', 0)}\nYangilanish: {updated_at}"

                bot.send_message(
                    message.chat.id,
                    welcome_text,
                    reply_markup=get_main_menu(user_id, is_admin)
                )
            else:
                # Yangi foydalanuvchi
                welcome_text = f"Assalomu alaykum {user_name}!\nSochiq renting servisiga xush kelibsiz!\n\nRo'yxatdan o'tish uchun quyidagi tugmani bosing."
                bot.send_message(
                    message.chat.id,
                    welcome_text,
                    reply_markup=get_register_keyboard()
                )

    @bot.message_handler(func=lambda message: message.text == "📝 Ro'yxatdan o'tish")
    def register_handler(message: Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name

        # Foydalanuvchini tekshirish
        with DatabaseService() as db_service:
            existing_user = db_service.get_user_by_telegram_id(user_id)
            if existing_user:
                bot.send_message(
                    message.chat.id,
                    "Siz allaqachon ro'yxatdan o'tgansiz! ✅",
                    reply_markup=get_main_menu(user_id)
                )
                return

        # Ro'yxatdan o'tish jarayonini boshlash
        user_registration_data[user_id] = {
            'step': 'name',
            'name': user_name
        }

        bot.send_message(
            message.chat.id,
            "Iltimos, to'liq ismingizni kiriting:",
            reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(user_name))
        )

    @bot.message_handler(func=lambda message:
    message.from_user.id in user_registration_data and
    user_registration_data[message.from_user.id]['step'] == 'name')
    def get_name_handler(message: Message):
        user_id = message.from_user.id
        user_registration_data[user_id]['name'] = message.text
        user_registration_data[user_id]['step'] = 'phone'

        # Telefon raqamini so'rash
        phone_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        phone_keyboard.add(KeyboardButton("📞 Telefon raqamimni yuborish", request_contact=True))

        bot.send_message(
            message.chat.id,
            "Iltimos, telefon raqamingizni yuboring:",
            reply_markup=phone_keyboard
        )

    @bot.message_handler(content_types=['contact'],
                         func=lambda message:
                         message.from_user.id in user_registration_data and
                         user_registration_data[message.from_user.id]['step'] == 'phone')
    def get_phone_contact_handler(message: Message):
        user_id = message.from_user.id
        if message.contact:
            user_registration_data[user_id]['phone_number'] = message.contact.phone_number
            user_registration_data[user_id]['step'] = 'complete'

            # Ma'lumotlarni yig'dik, endi database ga yaratamiz
            with DatabaseService() as db_service:
                data = user_registration_data[user_id]
                result = db_service.create_user(
                    name=data['name'],
                    telegram_id=user_id,
                    phone_number=data.get('phone_number')
                )

                if result:
                    bot.send_message(
                        message.chat.id,
                        f"🎉 Tabriklaymiz! Ro'yxatdan muvaffaqiyatli o'tdingiz.\n\n"
                        f"📋 Ma'lumotlaringiz:\n"
                        f"👤 Ism: {data['name']}\n"
                        f"📞 Telefon: {data.get('phone_number', 'Kiritilmagan')}\n\n"
                        f"Endi siz sochiq renting tizimidan foydalana olasiz!",
                        reply_markup=get_main_menu(user_id)
                    )
                else:
                    bot.send_message(
                        message.chat.id,
                        "Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
                    )

            # Ma'lumotlarni tozalash
            if user_id in user_registration_data:
                del user_registration_data[user_id]

    @bot.message_handler(func=lambda message:
    message.from_user.id in user_registration_data and
    user_registration_data[message.from_user.id]['step'] == 'phone')
    def get_phone_text_handler(message: Message):
        user_id = message.from_user.id
        user_registration_data[user_id]['phone_number'] = message.text
        user_registration_data[user_id]['step'] = 'complete'

        # Ma'lumotlarni yig'dik, endi database ga yaratamiz
        with DatabaseService() as db_service:
            data = user_registration_data[user_id]
            result = db_service.create_user(
                name=data['name'],
                telegram_id=user_id,
                phone_number=data.get('phone_number')
            )

            if result:
                bot.send_message(
                    message.chat.id,
                    f"🎉 Tabriklaymiz! Ro'yxatdan muvaffaqiyatli o'tdingiz.\n\n"
                    f"📋 Ma'lumotlaringiz:\n"
                    f"👤 Ism: {data['name']}\n"
                    f"📞 Telefon: {data.get('phone_number', 'Kiritilmagan')}\n\n"
                    f"Endi siz sochiq renting tizimidan foydalana olasiz!",
                    reply_markup=get_main_menu(user_id)
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "Ro'yxatdan o'tishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
                )

        # Ma'lumotlarni tozalash
        if user_id in user_registration_data:
            del user_registration_data[user_id]