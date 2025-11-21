from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.service import DatabaseService
from utils.keyboards import get_admin_menu, get_report_periods, get_inventory_management_keyboard
from utils.helpers import format_date
from utils.ai_service import ai_service
from config import ADMIN_IDS

# Sochiq miqdor kiritish jarayonini kuzatish
user_action_data = {}
# Admin message sending state
admin_message_state = {}
# Inventory management state
inventory_action_state = {}
# AI report question state
ai_report_state = {}


def setup_admin_handlers(bot):
    def show_users_list(message: Message):
        """Foydalanuvchilar ro'yxatini inline buttonlar shaklida ko'rsatish"""
        with DatabaseService() as db_service:
            users = db_service.get_all_users()

            if not users:
                bot.send_message(message.chat.id, "Hozircha hech qanday foydalanuvchi yo'q.")
                return

            keyboard = InlineKeyboardMarkup(row_width=2)

            # Har bir foydalanuvchi uchun button qo'shamiz
            buttons = []
            for user in users:
                name = user.get('name', 'Noma\'lum')
                user_id = user.get('id')
                buttons.append(InlineKeyboardButton(name, callback_data=f"user_{user_id}"))

            # Buttonlarni qatorlarga joylashtirish
            for i in range(0, len(buttons), 2):
                if i + 1 < len(buttons):
                    keyboard.add(buttons[i], buttons[i + 1])
                else:
                    keyboard.add(buttons[i])

            bot.send_message(
                message.chat.id,
                "👥 Foydalanuvchilar ro'yxati\n\nQuyidagi foydalanuvchilardan birini tanlang:",
                reply_markup=keyboard
            )

    @bot.message_handler(func=lambda message: message.text == "👥 Sartaroshlar" and message.from_user.id in ADMIN_IDS)
    def users_list_handler(message: Message):
        show_users_list(message)

    # Foydalanuvchi tanlanganda batafsil ma'lumotlarni ko'rsatish
    @bot.callback_query_handler(func=lambda call: call.data.startswith('user_'))
    def user_detail_handler(call: CallbackQuery):
        user_id = call.data.replace('user_', '')
        
        with DatabaseService() as db_service:
            user = db_service.get_user(user_id)

            if not user:
                bot.answer_callback_query(call.id, "Foydalanuvchi topilmadi!")
                return

            name = user.get('name', 'Noma\'lum')
            phone = user.get('phone_number', 'Kiritilmagan')
            towel_count = user.get('towel_count', 0)
            updated_at = format_date(user.get('updated_at', ''))

            # Batafsil ma'lumotlar
            detail_text = (
                f"👤 {name}\n\n"
                f"📞 Telefon: {phone}\n"
                f"🧺 Sochiqlar soni: {towel_count} ta\n"
                f"📅 Yangilanish: {updated_at}"
            )

            # Amallar keyboard
            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("Sochiq berish ➕", callback_data=f"give_{user_id}"),
                InlineKeyboardButton("Sochiq olish ➖", callback_data=f"take_{user_id}"),
                InlineKeyboardButton("🔙 Foydalanuvchilar ro'yxati", callback_data="back_to_users_list")
            )

            bot.edit_message_text(
                detail_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode='Markdown'
            )

    # Sochiq berish/olish handlerlari
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('give_', 'take_')))
    def towel_action_handler(call: CallbackQuery):
        data_parts = call.data.split('_')
        action = data_parts[0]  # give yoki take
        user_id = data_parts[1]

        with DatabaseService() as db_service:
            user = db_service.get_user(user_id)
            if not user:
                bot.answer_callback_query(call.id, "Foydalanuvchi topilmadi!")
                return

            user_name = user.get('name', 'Noma\'lum')
            action_text = "berish" if action == 'give' else "olish"

            # Foydalanuvchi ma'lumotlarini saqlash
            user_action_data[call.from_user.id] = {
                'action': action,
                'user_id': user_id,
                'user_name': user_name
            }

            msg = bot.send_message(
                call.message.chat.id,
                f"{user_name} uchun sochiq {action_text} miqdorini kiriting (faqat raqamlar bilan):",
                parse_mode='Markdown'
            )

            # Keyingi qadamni kutish
            bot.register_next_step_handler(msg, process_towel_quantity, action, user_id, user_name)

    def process_towel_quantity(message: Message, action, user_id, user_name):
        """Sochiq miqdorini qayta ishlash"""
        try:
            # Faqat raqam tekshiruvi
            if not message.text.isdigit():
                bot.send_message(
                    message.chat.id,
                    "❌ Xato: Faqat raqam kiriting! Iltimos, miqdorni raqamlar bilan kiriting."
                )
                # Qayta urinish
                msg = bot.send_message(
                    message.chat.id,
                    f"**{user_name}** uchun sochiq {'berish' if action == 'give' else 'olish'} miqdorini kiriting:"
                )
                bot.register_next_step_handler(msg, process_towel_quantity, action, user_id, user_name)
                return

            quantity = int(message.text)

            if quantity <= 0:
                bot.send_message(message.chat.id, "❌ Miqdor 0 dan katta bo'lishi kerak!")
                return

            # Operatsiyani bajarish
            transaction_type = 'given' if action == 'give' else 'taken'
            
            with DatabaseService() as db_service:
                result = db_service.update_user_towel_count(user_id, transaction_type, quantity)

                if result:
                    # Yangilangan ma'lumotlarni olish
                    if isinstance(result, dict) and 'user' in result:
                        updated_user = result['user']
                    else:
                        updated_user = db_service.get_user(user_id)

                    towel_count = updated_user.get('towel_count', 0)

                    action_emoji = "✅" if action == 'give' else "❌"
                    action_text = "berildi" if action == 'give' else "olindi"
                    operation_type_text = "oldingiz" if action == 'give' else "berdingiz"

                    # Admin uchun xabar
                    admin_success_text = (
                        f"{action_emoji} Operatsiya muvaffaqiyatli!\n\n"
                        f"👤 Foydalanuvchi: {user_name}\n"
                        f"📦 Amal: Sochiq {action_text}\n"
                        f"🔢 Miqdor: {quantity} ta\n"
                        f"🧺 Yangi soni: {towel_count} ta"
                    )

                    bot.send_message(message.chat.id, admin_success_text)

                    # Foydalanuvchiga batafsil xabar yuborish
                    try:
                        user_telegram_id = updated_user.get('telegram_id')
                        if user_telegram_id:
                            if action == 'give':  # Sochiq BERILGANDA
                                user_message = (
                                    f"🎉 Yangi sochiq olindi\n\n"
                                    f"📅 Bugun siz {quantity} ta sochiq {operation_type_text}\n\n"
                                    f"📊 Joriy holat:\n"
                                    f"🧺 Sochiqlar soni: {towel_count} ta"
                                )
                            else:  # Sochiq OLINGANDA
                                user_message = (
                                    f"🔔 Sochiq berildi\n\n"
                                    f"📅 Bugun siz {quantity} ta sochiq {operation_type_text}\n\n"
                                    f"📊 Joriy holat:\n"
                                    f"🧺 Sochiqlar soni: {towel_count} ta"
                                )

                            bot.send_message(user_telegram_id, user_message)
                    except Exception as e:
                        print(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
                else:
                    bot.send_message(message.chat.id, "❌ Operatsiyada xatolik yuz berdi!")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Xato yuz berdi: {e}")

    # Foydalanuvchilar ro'yxatiga qaytish
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_users_list')
    def back_to_users_handler(call: CallbackQuery):
        # O'rniga yangi xabar yuboramiz
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass  # Agar xabarni o'chirib bo'lmasa, davom etamiz

        # Yangi xabar yuborish
        show_users_list(call.message)

    # Ombor handleri
    @bot.message_handler(func=lambda message: message.text == "📦 Ombor" and message.from_user.id in ADMIN_IDS)
    def inventory_handler(message: Message):
        with DatabaseService() as db_service:
            inventory = db_service.get_inventory()

            if not inventory:
                inventory_data = {'total_towels': 0, 'remaining_towels': 0, 'last_updated': ''}
            else:
                inventory_data = inventory

            total = inventory_data.get('total_towels', 0)
            remaining = inventory_data.get('remaining_towels', 0)
            used = total - remaining

            # Vaqtni formatlash
            last_updated = format_date(inventory_data.get('last_updated', ''))

            response_text = (
                "📦 Ombor holati\n\n"
                f"📊 Jami sochiqlar: {total} ta\n"
                f"✅ Qolgan sochiqlar: {remaining} ta\n"
                f"🔄 Foydalanilgan: {used} ta\n"
                f"📅 Oxirgi yangilanish: {last_updated}\n\n"
                f"Omborni boshqarish uchun quyidagi tugmalardan foydalaning:"
            )

            bot.send_message(
                message.chat.id, 
                response_text, 
                reply_markup=get_inventory_management_keyboard()
            )

    # Ombor boshqaruv callback handlerlari
    @bot.callback_query_handler(func=lambda call: call.data.startswith('inv_'))
    def inventory_management_handler(call: CallbackQuery):
        if call.data == 'inv_add':
            # Sochiq qo'shish
            inventory_action_state[call.from_user.id] = {'action': 'add'}
            bot.send_message(
                call.message.chat.id,
                "➕ Sochiq qo'shish\n\nQancha sochiq qo'shmoqchisiz? (faqat raqamlar bilan):"
            )
            bot.register_next_step_handler(call.message, process_inventory_action, 'add')
            bot.answer_callback_query(call.id)

        elif call.data == 'inv_remove':
            # Eskirgan sochiqlarni olib tashlash
            inventory_action_state[call.from_user.id] = {'action': 'remove'}
            bot.send_message(
                call.message.chat.id,
                "➖ Eskirgan sochiqlarni olib tashlash\n\nQancha eskirgan sochiqni olib tashlamoqchisiz? (faqat raqamlar bilan):"
            )
            bot.register_next_step_handler(call.message, process_inventory_action, 'remove')
            bot.answer_callback_query(call.id)

        elif call.data == 'inv_back':
            # Orqaga qaytish
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            # Ombor holatini qayta ko'rsatish
            with DatabaseService() as db_service:
                inventory = db_service.get_inventory()
                if not inventory:
                    inventory_data = {'total_towels': 0, 'remaining_towels': 0, 'last_updated': ''}
                else:
                    inventory_data = inventory

                total = inventory_data.get('total_towels', 0)
                remaining = inventory_data.get('remaining_towels', 0)
                used = total - remaining
                last_updated = format_date(inventory_data.get('last_updated', ''))

                response_text = (
                    "📦 Ombor holati\n\n"
                    f"📊 Jami sochiqlar: {total} ta\n"
                    f"✅ Qolgan sochiqlar: {remaining} ta\n"
                    f"🔄 Foydalanilgan: {used} ta\n"
                    f"📅 Oxirgi yangilanish: {last_updated}\n\n"
                    f"Omborni boshqarish uchun quyidagi tugmalardan foydalaning:"
                )

                bot.send_message(
                    call.message.chat.id,
                    response_text,
                    reply_markup=get_inventory_management_keyboard()
                )
            bot.answer_callback_query(call.id)

    def process_inventory_action(message: Message, action: str):
        """Ombor operatsiyasini qayta ishlash"""
        try:
            # Faqat raqam tekshiruvi
            if not message.text.isdigit():
                bot.send_message(
                    message.chat.id,
                    "❌ Xato: Faqat raqam kiriting! Iltimos, miqdorni raqamlar bilan kiriting."
                )
                # Qayta urinish
                action_text = "qo'shmoqchisiz" if action == 'add' else "olib tashlamoqchisiz"
                msg = bot.send_message(
                    message.chat.id,
                    f"Qancha sochiq {action_text}? (faqat raqamlar bilan):"
                )
                bot.register_next_step_handler(msg, process_inventory_action, action)
                return

            quantity = int(message.text)

            if quantity <= 0:
                bot.send_message(message.chat.id, "❌ Miqdor 0 dan katta bo'lishi kerak!")
                return

            # Operatsiyani bajarish
            with DatabaseService() as db_service:
                if action == 'add':
                    result = db_service.add_towels_to_inventory(quantity)
                    action_text = "qo'shildi"
                    action_emoji = "✅"
                else:  # remove
                    # Tekshirish - omborda yetarli sochiq bormi?
                    current_inventory = db_service.get_inventory()
                    if current_inventory and quantity > current_inventory.get('total_towels', 0):
                        bot.send_message(
                            message.chat.id,
                            f"❌ Xato: Omborda faqat {current_inventory.get('total_towels', 0)} ta sochiq bor!"
                        )
                        return
                    result = db_service.remove_towels_from_inventory(quantity)
                    action_text = "olib tashlandi"
                    action_emoji = "🗑️"

                if result:
                    total = result.get('total_towels', 0)
                    remaining = result.get('remaining_towels', 0)
                    used = total - remaining

                    success_text = (
                        f"{action_emoji} Operatsiya muvaffaqiyatli!\n\n"
                        f"📦 Amal: {quantity} ta sochiq {action_text}\n\n"
                        f"📊 Yangi ombor holati:\n"
                        f"📊 Jami sochiqlar: {total} ta\n"
                        f"✅ Qolgan sochiqlar: {remaining} ta\n"
                        f"🔄 Foydalanilgan: {used} ta"
                    )

                    bot.send_message(
                        message.chat.id,
                        success_text,
                        reply_markup=get_inventory_management_keyboard()
                    )
                else:
                    bot.send_message(message.chat.id, "❌ Operatsiyada xatolik yuz berdi!")

            # State ni tozalash
            if message.from_user.id in inventory_action_state:
                del inventory_action_state[message.from_user.id]

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Xato yuz berdi: {e}")
            if message.from_user.id in inventory_action_state:
                del inventory_action_state[message.from_user.id]

    # Hisobotlar handleri
    @bot.message_handler(func=lambda message: message.text == "📊 Hisobotlar" and message.from_user.id in ADMIN_IDS)
    def reports_handler(message: Message):
        response_text = (
            "📊 Hisobotlar\n\n"
            "Quyidagi davrlar bo'yicha hisobotlarni ko'rishingiz mumkin:"
        )

        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Bugun", callback_data="report_today"),
            InlineKeyboardButton("So'nggi 7 kun", callback_data="report_week"),
            InlineKeyboardButton("So'nggi oy", callback_data="report_month"),
            InlineKeyboardButton("Hamma vaqt", callback_data="report_all"),
            InlineKeyboardButton("🤖 AI Hisobot", callback_data="report_ai")
        )

        bot.send_message(
            message.chat.id,
            response_text,
            reply_markup=keyboard
        )

    # Hisobotlar callback handler
    @bot.callback_query_handler(func=lambda call: call.data.startswith('report_'))
    def report_callback_handler(call: CallbackQuery):
        if call.data == 'report_ai':
            # AI hisobot uchun - avval admin savolini so'raymiz
            bot.answer_callback_query(call.id)

            ai_report_state[call.from_user.id] = {"awaiting_question": True}

            msg = bot.send_message(
                call.message.chat.id,
                (
                    "🤖 AI Hisobot\n\n"
                    "Savolingizni yozing. Masalan:\n"
                    "- Kecha barber_a ga nechta sochiq berdim?\n"
                    "- So'nggi 7 kunda eng ko'p sochiq olgan sartarosh kim?\n\n"
                    "AI ma'lumotlarni bazadan oladi va O'zbekiston vaqti (UTC+5) bo'yicha "
                    "hisoblab javob beradi."
                )
            )

            # Keyingi qadamda AI savolini qayta ishlaymiz
            bot.register_next_step_handler(msg, process_ai_report_question)
            return

        period = call.data.replace('report_', '')
        period_names = {
            'today': 'Bugun',
            'week': "So'nggi 7 kun",
            'month': "So'nggi oy",
            'all': 'Hamma vaqt'
        }

        with DatabaseService() as db_service:
            report = db_service.get_report(period)

            if not report:
                bot.answer_callback_query(call.id, "Hisobot olishda xatolik!")
                return

            given_towels = report.get('given_towels', 0)
            taken_towels = report.get('taken_towels', 0)
            total_transactions = report.get('total_transactions', 0)

            response_text = (
                f"📊 {period_names.get(period, period)} hisoboti\n\n"
                f"✅ Berilgan sochiqlar: {given_towels} ta\n"
                f"❌ Olingan sochiqlar: {taken_towels} ta\n"
                f"📈 Jami operatsiyalar: {total_transactions} ta\n"
                f"📅 Davr: {report.get('start_date', '')[:10]} - {report.get('end_date', '')[:10]}"
            )

            keyboard = InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                InlineKeyboardButton("Bugun", callback_data="report_today"),
                InlineKeyboardButton("So'nggi 7 kun", callback_data="report_week"),
                InlineKeyboardButton("So'nggi oy", callback_data="report_month"),
                InlineKeyboardButton("Hamma vaqt", callback_data="report_all"),
                InlineKeyboardButton("🤖 AI Hisobot", callback_data="report_ai")
            )

            bot.edit_message_text(
                response_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard
            )

    def process_ai_report_question(message: Message):
        """Adminning AI hisobot savolini qayta ishlash"""
        admin_id = message.from_user.id

        # Faqat adminlar uchun
        if admin_id not in ADMIN_IDS:
            bot.send_message(message.chat.id, "❌ Siz bu funksiyadan foydalana olmaysiz.")
            return

        # State tekshirish
        if admin_id not in ai_report_state or not ai_report_state[admin_id].get("awaiting_question"):
            bot.send_message(message.chat.id, "⚠️ AI hisobot uchun avval '📊 Hisobotlar' → '🤖 AI Hisobot' ni bosing.")
            return

        question_text = message.text.strip()
        if not question_text:
            bot.send_message(message.chat.id, "❌ Iltimos, savolni matn ko'rinishida yuboring.")
            return

        bot.send_message(message.chat.id, "⏳ AI hisobot tayyorlanmoqda, iltimos kuting...")

        # Bazadan kerakli ma'lumotlarni olamiz
        with DatabaseService() as db_service:
            try:
                users = db_service.get_all_users()
                # Cheklangan miqdordagi tranzaksiyalarni olamiz (masalan, oxirgi 1000 ta)
                transactions = db_service.get_all_transactions_with_users(limit=1000)
                inventory = db_service.get_inventory()

                data_for_ai = {
                    "users": users,
                    "transactions": transactions,
                    "inventory": inventory,
                }
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ma'lumotlarni bazadan olishda xatolik: {e}")
                if admin_id in ai_report_state:
                    del ai_report_state[admin_id]
                return

        # AI dan javob olish
        ai_answer = ai_service.answer_question_with_data(question_text, data_for_ai)

        bot.send_message(
            message.chat.id,
            f"🤖 AI Javobi\n\n{ai_answer}"
        )

        # State ni tozalash
        if admin_id in ai_report_state:
            del ai_report_state[admin_id]

    # Admin xabar yuborish funksiyasi
    @bot.message_handler(func=lambda message: message.text == "💬 Xabar yuborish" and message.from_user.id in ADMIN_IDS)
    def admin_message_handler(message: Message):
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📢 Barcha foydalanuvchilarga", callback_data="msg_all"),
            InlineKeyboardButton("👤 Tanlangan foydalanuvchiga", callback_data="msg_select")
        )
        bot.send_message(
            message.chat.id,
            "📨 Xabar yuborish\n\nQaysi foydalanuvchilarga xabar yubormoqchisiz?",
            reply_markup=keyboard
        )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('msg_'))
    def admin_message_callback(call: CallbackQuery):
        if call.data == 'msg_all':
            admin_message_state[call.from_user.id] = {'type': 'all'}
            bot.send_message(
                call.message.chat.id,
                "📝 Xabaringizni kiriting (barcha foydalanuvchilarga yuboriladi):"
            )
            bot.register_next_step_handler(call.message, process_admin_message, 'all')
        elif call.data == 'msg_select':
            # Foydalanuvchilar ro'yxatini ko'rsatish
            with DatabaseService() as db_service:
                users = db_service.get_all_users()
                if not users:
                    bot.answer_callback_query(call.id, "Foydalanuvchilar topilmadi!")
                    return

                keyboard = InlineKeyboardMarkup(row_width=1)
                for user in users:
                    name = user.get('name', 'Noma\'lum')
                    user_id = user.get('id')
                    keyboard.add(InlineKeyboardButton(name, callback_data=f"msg_user_{user_id}"))

                bot.edit_message_text(
                    "👤 Foydalanuvchini tanlang:",
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard
                )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('msg_user_'))
    def select_user_for_message(call: CallbackQuery):
        user_id = call.data.replace('msg_user_', '')
        admin_message_state[call.from_user.id] = {'type': 'selected', 'user_id': user_id}
        bot.send_message(
            call.message.chat.id,
            "📝 Xabaringizni kiriting:"
        )
        bot.register_next_step_handler(call.message, process_admin_message, 'selected', user_id)

    def process_admin_message(message: Message, msg_type, user_id=None):
        """Admin xabarini qayta ishlash"""
        admin_id = message.from_user.id
        message_text = message.text

        if msg_type == 'all':
            # Barcha foydalanuvchilarga yuborish
            with DatabaseService() as db_service:
                users = db_service.get_all_users()
                sent = 0
                failed = 0

                for user in users:
                    try:
                        telegram_id = user.get('telegram_id')
                        bot.send_message(telegram_id, f"📨 Admin xabari:\n\n{message_text}")
                        sent += 1
                    except Exception as e:
                        failed += 1
                        print(f"Xabar yuborishda xatolik (telegram_id: {telegram_id}): {e}")

                bot.send_message(
                    admin_id,
                    f"✅ Xabar yuborildi!\n\nYuborildi: {sent} ta\nXatolik: {failed} ta"
                )
        else:
            # Tanlangan foydalanuvchiga yuborish
            with DatabaseService() as db_service:
                user = db_service.get_user(user_id)
                if user:
                    try:
                        telegram_id = user.get('telegram_id')
                        bot.send_message(telegram_id, f"📨 Admin xabari:\n\n{message_text}")
                        bot.send_message(admin_id, f"✅ Xabar {user.get('name')} ga muvaffaqiyatli yuborildi!")
                    except Exception as e:
                        bot.send_message(admin_id, f"❌ Xabar yuborishda xatolik: {e}")
                else:
                    bot.send_message(admin_id, "❌ Foydalanuvchi topilmadi!")

        # State ni tozalash
        if admin_id in admin_message_state:
            del admin_message_state[admin_id]
