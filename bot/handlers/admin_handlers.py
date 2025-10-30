from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.api_client import api_client
from utils.keyboards import (
    get_admin_menu, get_report_periods
)
from utils.helpers import format_date
from config import ADMIN_IDS

# Narxni o'zgartirish va miqdor kiritish jarayonini kuzatish
user_action_data = {}


def setup_admin_handlers(bot):
    def show_barbers_list(message: Message):
        """Sartaroshlar ro'yxatini inline buttonlar shaklida ko'rsatish"""
        barbers = api_client.get_barbers()

        if not barbers:
            bot.send_message(message.chat.id, "Hozircha hech qanday sartarosh yo'q.")
            return

        keyboard = InlineKeyboardMarkup(row_width=2)

        # Har bir sartarosh uchun button qo'shamiz
        buttons = []
        for barber in barbers:
            name = barber.get('name', 'Noma\'lum')
            barber_id = barber.get('id')
            buttons.append(InlineKeyboardButton(name, callback_data=f"barber_{barber_id}"))

        # Buttonlarni qatorlarga joylashtirish
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.add(buttons[i], buttons[i + 1])
            else:
                keyboard.add(buttons[i])

        bot.send_message(
            message.chat.id,
            "👥 Sartaroshlar ro'yxati\n\nQuyidagi sartaroshlardan birini tanlang:",
            reply_markup=keyboard
        )

    @bot.message_handler(func=lambda message: message.text == "👥 Sartaroshlar" and message.from_user.id in ADMIN_IDS)
    def barbers_list_handler(message: Message):
        show_barbers_list(message)

    # Sartarosh tanlanganda batafsil ma'lumotlarni ko'rsatish
    @bot.callback_query_handler(func=lambda call: call.data.startswith('barber_'))
    def barber_detail_handler(call: CallbackQuery):
        barber_id = call.data.replace('barber_', '')
        barber = api_client.get_barber(barber_id)

        if not barber:
            bot.answer_callback_query(call.id, "Sartarosh topilmadi!")
            return

        name = barber.get('name', 'Noma\'lum')
        phone = barber.get('phone_number', 'Kiritilmagan')
        barbershop = barber.get('barbershop_name', 'Kiritilmagan')
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

        # Batafsil ma'lumotlar
        detail_text = (
            f"👤 {name}\n\n"
            f"📞 Telefon: {phone}\n"
            f"🏪 Sartaroshxona: {barbershop}\n"
            f"🧺 Sochiqlar soni: {towel_count} ta\n"
            f"💰 Sochiq narxi: {towel_price:,.0f} so'm\n"
            f"💵 Jami qiymat: {total_value:,.0f} so'm\n"
            f"📅 Yangilanish: {updated_at}"
        )

        # Amallar keyboard
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Sochiq berish ➕", callback_data=f"give_{barber_id}"),
            InlineKeyboardButton("Sochiq olish ➖", callback_data=f"take_{barber_id}"),
            InlineKeyboardButton("Narxni o'zgartirish 💰", callback_data=f"price_{barber_id}"),
            InlineKeyboardButton("🔙 Sartaroshlar ro'yxati", callback_data="back_to_barbers_list")
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
        barber_id = data_parts[1]

        barber = api_client.get_barber(barber_id)
        if not barber:
            bot.answer_callback_query(call.id, "Sartarosh topilmadi!")
            return

        barber_name = barber.get('name', 'Noma\'lum')
        action_text = "berish" if action == 'give' else "olish"

        # Foydalanuvchi ma'lumotlarini saqlash
        user_action_data[call.from_user.id] = {
            'action': action,
            'barber_id': barber_id,
            'barber_name': barber_name
        }

        msg = bot.send_message(
            call.message.chat.id,
            f"{barber_name} uchun sochiq {action_text} miqdorini kiriting (faqat raqamlar bilan):",
            parse_mode='Markdown'
        )

        # Keyingi qadamni kutish
        bot.register_next_step_handler(msg, process_towel_quantity, action, barber_id, barber_name)

    def process_towel_quantity(message: Message, action, barber_id, barber_name):
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
                    f"**{barber_name}** uchun sochiq {'berish' if action == 'give' else 'olish'} miqdorini kiriting:"
                )
                bot.register_next_step_handler(msg, process_towel_quantity, action, barber_id, barber_name)
                return

            quantity = int(message.text)

            if quantity <= 0:
                bot.send_message(message.chat.id, "❌ Miqdor 0 dan katta bo'lishi kerak!")
                return

            # Operatsiyani bajarish
            transaction_type = 'given' if action == 'give' else 'taken'
            result = api_client.update_barber_towels(barber_id, transaction_type, quantity)

            if result:
                # Yangilangan ma'lumotlarni olish
                if isinstance(result, dict) and 'barber' in result:
                    updated_barber = result['barber']
                else:
                    updated_barber = api_client.get_barber(barber_id)

                towel_count = updated_barber.get('towel_count', 0)

                # towel_price ni to'g'ri formatda olish
                towel_price = updated_barber.get('towel_price', 0)
                try:
                    if isinstance(towel_price, str):
                        towel_price = float(towel_price)
                except (ValueError, TypeError):
                    towel_price = 0

                total_value = towel_count * towel_price
                operation_value = quantity * towel_price

                action_emoji = "✅" if action == 'give' else "❌"
                action_text = "berildi" if action == 'give' else "olindi"
                operation_type_text = "oldingiz" if action == 'give' else "berdingiz"

                # Admin uchun xabar
                admin_success_text = (
                    f"{action_emoji} Operatsiya muvaffaqiyatli!\n\n"
                    f"👤 Sartarosh: {barber_name}\n"
                    f"📦 Amal: Sochiq {action_text}\n"
                    f"🔢 Miqdor: {quantity} ta\n"
                    f"🧺 Yangi soni: {towel_count} ta\n"
                    f"💰 Operatsiya qiymati: {operation_value:,.0f} so'm"
                )

                bot.send_message(message.chat.id, admin_success_text)

                # Sartaroshga batafsil xabar yuborish
                try:
                    barber_telegram_id = updated_barber.get('telegram_id')
                    if barber_telegram_id:
                        if action == 'give':  # Sochiq BERILGANDA
                            barber_message = (
                                f"🎉 Yangi sochiq olindi\n\n"
                                f"📅 Bugun siz {quantity} ta sochiq {operation_type_text}\n"
                                f"💰 Umumiy narxi: {operation_value:,.0f} so'm\n\n"
                                f"📊 Joriy holat:\n"
                                f"🧺 Sochiqlar soni: {towel_count} ta\n"
                                f"💵 Jami qiymati: {total_value:,.0f} so'm\n\n"
                                f"💎 Sochiq narxi: {towel_price:,.0f} so'm/ta"
                            )
                        else:  # Sochiq OLINGANDA
                            barber_message = (
                                f"🔔 Sochiq berildi\n\n"
                                f"📅 Bugun siz {quantity} ta sochiq {operation_type_text}\n"
                                f"💰 Umumiy narxi: {operation_value:,.0f} so'm\n\n"
                                f"📊 Joriy holat:\n"
                                f"🧺 Sochiqlar soni: {towel_count} ta\n"
                                f"💵 Jami qiymati: {total_value:,.0f} so'm\n\n"
                                f"💎 Sochiq narxi: {towel_price:,.0f} so'm/ta"
                            )

                        bot.send_message(barber_telegram_id, barber_message)
                        # print(f"Sartaroshga xabar muvaffaqiyatli yuborildi: {barber_telegram_id}")
                except Exception as e:
                    print(f"Sartaroshga xabar yuborishda xatolik: {e}")
            else:
                bot.send_message(message.chat.id, "❌ Operatsiyada xatolik yuz berdi!")

        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Xato yuz berdi: {e}")

    # Narxni o'zgartirish handleri
    @bot.callback_query_handler(func=lambda call: call.data.startswith('price_'))
    def price_callback_handler(call: CallbackQuery):
        barber_id = call.data.replace('price_', '')
        barber = api_client.get_barber(barber_id)

        if not barber:
            bot.answer_callback_query(call.id, "Sartarosh topilmadi!")
            return

        current_price = barber.get('towel_price', 2000)
        barber_name = barber.get('name', 'Noma\'lum')

        user_action_data[call.from_user.id] = {
            'action': 'price_change',
            'barber_id': barber_id,
            'barber_name': barber_name
        }

        msg = bot.send_message(
            call.message.chat.id,
            f"{barber_name} uchun yangi sochiq narxini kiriting (so'mda, faqat raqamlar bilan):\n"
            f"Joriy narx: {current_price:,} so'm",
            parse_mode='Markdown'
        )

        bot.register_next_step_handler(msg, process_price_change, barber_id, barber_name)

    def process_price_change(message: Message, barber_id, barber_name):
        """Narxni qayta ishlash"""
        try:
            # Faqat raqam tekshiruvi
            if not message.text.replace('.', '').isdigit():  # Nuqtani hisobga olgan holda
                bot.send_message(
                    message.chat.id,
                    "❌ Xato: Faqat raqam kiriting! Iltimos, narxni raqamlar bilan kiriting."
                )
                # Qayta urinish
                msg = bot.send_message(
                    message.chat.id,
                    f"**{barber_name}** uchun yangi sochiq narxini kiriting:"
                )
                bot.register_next_step_handler(msg, process_price_change, barber_id, barber_name)
                return

            new_price = float(message.text)

            if new_price <= 0:
                bot.send_message(message.chat.id, "❌ Narx musbat son bo'lishi kerak!")
                return

            # API orqali narxni yangilash
            result = api_client.update_barber_price(barber_id, new_price)
            if result:
                bot.send_message(
                    message.chat.id,
                    f"✅ {barber_name} uchun sochiq narxi muvaffaqiyatli yangilandi!\n"
                    f"Yangi narx: {new_price:,} so'm"
                )

                # Foydalanuvchiga xabar berish
                barber = api_client.get_barber(barber_id)
                barber_telegram_id = barber.get('telegram_id')
                if barber_telegram_id:
                    try:
                        bot.send_message(
                            barber_telegram_id,
                            f"🔔 Ogohlantirish\n\n"
                            f"Sizning sochiq narxingiz yangilandi.\n"
                            f"Yangi narx: {new_price:,} so'm"
                        )
                    except Exception as e:
                        print(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
            else:
                bot.send_message(message.chat.id, "❌ Narxni yangilashda xatolik yuz berdi!")

        except ValueError:
            bot.send_message(message.chat.id, "❌ Iltimos, narxni to'g'ri formatda kiriting!")

    # Sartaroshlar ro'yxatiga qaytish
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_barbers_list')
    def back_to_barbers_handler(call: CallbackQuery):
        # O'rniga yangi xabar yuboramiz
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass  # Agar xabarni o'chirib bo'lmasa, davom etamiz

        # Yangi xabar yuborish
        show_barbers_list(call.message)

    # Qolgan handlerlar (Ombor va Hisobotlar)
    @bot.message_handler(func=lambda message: message.text == "📦 Ombor" and message.from_user.id in ADMIN_IDS)
    def inventory_handler(message: Message):
        inventory = api_client.get_inventory()

        if not inventory:
            inventory_data = {'total_towels': 0, 'remaining_towels': 0, 'last_updated': ''}
        else:
            inventory_data = inventory[0] if isinstance(inventory, list) else inventory

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
            f"📅 Oxirgi yangilanish: {last_updated}"
        )

        bot.send_message(message.chat.id, response_text, reply_markup=get_admin_menu())

    @bot.message_handler(func=lambda message: message.text == "📊 Hisobotlar" and message.from_user.id in ADMIN_IDS)
    def reports_handler(message: Message):
        response_text = (
            "📊 Hisobotlar\n\n"
            "Quyidagi davrlar bo'yicha hisobotlarni ko'rishingiz mumkin:"
        )

        bot.send_message(
            message.chat.id,
            response_text,
            reply_markup=get_report_periods()
        )

    # Hisobotlar callback handler
    @bot.callback_query_handler(func=lambda call: call.data.startswith('report_'))
    def report_callback_handler(call: CallbackQuery):
        period = call.data.replace('report_', '')
        period_names = {
            'today': 'Bugun',
            'week': "So'nggi 7 kun",
            'month': "So'nggi oy",
            'all': 'Hamma vaqt'
        }

        report = api_client.get_report(period)

        if not report:
            bot.answer_callback_query(call.id, "Hisobot olishda xatolik!")
            return

        given_towels = report.get('given_towels', 0)
        taken_towels = report.get('taken_towels', 0)
        total_income = report.get('total_income', 0)

        # Formatlashda xatolikni oldini olish
        try:
            total_income_formatted = f"{float(total_income):,}" if total_income else "0"
        except (ValueError, TypeError):
            total_income_formatted = "0"

        response_text = (
            f"📊 {period_names.get(period, period)} hisoboti\n\n"
            f"✅ Berilgan sochiqlar: {given_towels} ta\n"
            f"❌ Olingan sochiqlar: {taken_towels} ta\n"
            f"💰 Daromad: {total_income_formatted} so'm\n"
            f"📅 Davr: {report.get('start_date', '')} - {report.get('end_date', '')}"
        )

        bot.edit_message_text(
            response_text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=get_report_periods()
        )