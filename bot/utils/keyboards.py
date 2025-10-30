from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu(telegram_id, is_admin=False):
    """Asosiy menu keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    if is_admin:
        keyboard.add(
            KeyboardButton("👥 Sartaroshlar"),
            KeyboardButton("📦 Ombor"),
            KeyboardButton("📊 Hisobotlar")
        )
    else:
        keyboard.add(
            KeyboardButton("🧺 Mening sochiqlarim"),
            KeyboardButton("📋 Mening tarixim")
        )

    return keyboard


def get_admin_menu():
    """Admin menu keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("👥 Sartaroshlar"),
        KeyboardButton("📦 Ombor"),
        KeyboardButton("📊 Hisobotlar"),
        KeyboardButton("🔙 Asosiy menu")
    )
    return keyboard


def get_report_periods():
    """Hisobot davrlari keyboard"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Bugun", callback_data="report_today"),
        InlineKeyboardButton("So'nggi 7 kun", callback_data="report_week"),
        InlineKeyboardButton("So'nggi oy", callback_data="report_month"),
        InlineKeyboardButton("Hamma vaqt", callback_data="report_all")
    )
    return keyboard


def get_register_keyboard():
    """Ro'yxatdan o'tish keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(KeyboardButton("📝 Ro'yxatdan o'tish"))
    return keyboard


def get_back_to_main():
    """Asosiy menu ga qaytish keyboard"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔙 Asosiy menu"))
    return keyboard