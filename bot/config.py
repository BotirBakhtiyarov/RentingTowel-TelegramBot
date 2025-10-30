import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
API_URL = os.getenv('API_URL', 'http://localhost:8000/api')
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else []

DJANGO_USERNAME = os.getenv('DJANGO_USERNAME', 'admin')
DJANGO_PASSWORD = os.getenv('DJANGO_PASSWORD', 'password')