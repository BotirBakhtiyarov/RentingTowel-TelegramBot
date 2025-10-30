import requests
import json
from config import API_URL, DJANGO_USERNAME, DJANGO_PASSWORD


class APIClient:
    def __init__(self):
        self.base_url = API_URL
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """Django REST API uchun autentifikatsiya"""
        try:
            self.session.auth = (DJANGO_USERNAME, DJANGO_PASSWORD)
        except Exception as e:
            print(f"Auth error: {e}")

    def _make_request(self, method, endpoint, data=None):
        """Umumiy so'rov metod"""
        url = f"{self.base_url}/{endpoint}/"
        try:
            if method == 'GET':
                response = self.session.get(url, params=data)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'PATCH':
                response = self.session.patch(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)

            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            print(f"API request error: {e}")
            return None

    def _get_results(self, data):
        """Ma'lumotlarni to'g'ri formatda olish"""
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('results', data)
        return data

    # Barber metodlari
    def get_barbers(self):
        result = self._make_request('GET', 'barbers')
        return self._get_results(result)

    def get_barber(self, barber_id):
        return self._make_request('GET', f'barbers/{barber_id}')

    def get_barber_by_telegram_id(self, telegram_id):
        barbers = self.get_barbers()
        if barbers:
            for barber in barbers:
                if barber.get('telegram_id') == telegram_id:
                    return barber
        return None

    def create_barber(self, name, telegram_id, phone_number=None, barbershop_name=None, towel_price=2000):
        data = {
            'name': name,
            'telegram_id': telegram_id,
            'phone_number': phone_number,
            'barbershop_name': barbershop_name,
            'towel_price': towel_price
        }
        return self._make_request('POST', 'barbers', data)

    def update_barber_price(self, barber_id, new_price):
        """Sartaroshning sochiq narxini yangilash"""
        data = {
            'towel_price': new_price
        }
        return self._make_request('PATCH', f'barbers/{barber_id}', data)

    def update_barber_towels(self, barber_id, transaction_type, quantity, admin_id=1):
        """Sochiq berish/olish operatsiyasi"""
        barber = self.get_barber(barber_id)
        if not barber:
            return None

        # Tranzaksiya yaratish
        transaction_data = {
            'barber': barber_id,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'notes': f'Telegram bot orqali'
        }

        # print(f"Transaction yaratilmoqda: {transaction_data}")

        result = self._make_request('POST', 'transactions', transaction_data)

        # Agar transaction muvaffaqiyatli yaratilsa, yangilangan barber ma'lumotlarini qaytarish
        if result:
            # Yangilangan barber ma'lumotlarini olish
            updated_barber = self.get_barber(barber_id)
            return {
                'transaction': result,
                'barber': updated_barber
            }
        return None

    def get_barber_transactions(self, barber_id):
        transactions = self._make_request('GET', 'transactions')
        transactions = self._get_results(transactions)

        if transactions:
            filtered_transactions = [t for t in transactions if t.get('barber') == barber_id]

            # Har bir transactionning total_price ni to'g'ri formatda qaytarish
            for transaction in filtered_transactions:
                if 'total_price' in transaction:
                    try:
                        transaction['total_price'] = float(transaction['total_price'])
                    except (ValueError, TypeError):
                        transaction['total_price'] = 0

            return filtered_transactions
        return []

    def get_inventory(self):
        result = self._make_request('GET', 'inventory')
        return self._get_results(result)

    def get_report(self, period='today'):
        return self._make_request('GET', 'reports', {'period': period})


# Global API client instance
api_client = APIClient()