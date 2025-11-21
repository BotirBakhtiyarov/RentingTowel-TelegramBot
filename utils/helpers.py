from datetime import datetime


def format_date(date_string):
    """Vaqtni '30.10.2025 00:00' formatiga o'tkazish"""
    if not date_string:
        return "Noma'lum"

    try:
        # ISO formatdagi vaqtni o'qish
        if 'T' in date_string:
            # "2025-10-30T20:43:00.123456Z" -> "30.10.2025 20:43"
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y %H:%M')
        else:
            # Agar boshqa format bo'lsa, sana va soatni ajratib olish
            if len(date_string) >= 16:
                # "2025-10-30 20:43:00" -> "30.10.2025 20:43"
                dt = datetime.strptime(date_string[:16], '%Y-%m-%d %H:%M')
                return dt.strftime('%d.%m.%Y %H:%M')
            else:
                # Faqat sana bo'lsa, soatni 00:00 qo'shamiz
                dt = datetime.strptime(date_string[:10], '%Y-%m-%d')
                return dt.strftime('%d.%m.%Y 00:00')
    except Exception as e:
        print(f"Vaqt formatlashda xato: {e}")
        return date_string[:16] if date_string else "Noma'lum"


def format_date_only(date_string):
    """Faqat sanani '30.10.2025' formatiga o'tkazish (tarix uchun)"""
    if not date_string:
        return "Noma'lum"

    try:
        if 'T' in date_string:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%d.%m.%Y')
        else:
            return date_string[:10].replace('-', '.')[8:10] + '.' + date_string[:10].replace('-', '.')[
                5:7] + '.' + date_string[:10].replace('-', '.')[:4]
    except Exception:
        return date_string[:10] if date_string else "Noma'lum"