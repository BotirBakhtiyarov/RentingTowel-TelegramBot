# README.md
![badge](https://img.shields.io/badge/License-MIT-yellow.svg)
![badge](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![badge](https://img.shields.io/badge/Django-4.2.7-green?logo=django&logoColor=white)
![badge](https://img.shields.io/badge/Architecture-Microservices-orange)
![telegram](https://img.shields.io/badge/pyTelegramBotAPI-4.15.2-26A5E4?logo=telegram&logoColor=white)
# Towel Renting Service - Telegram Bot & Django Backend

A comprehensive towel rental management system designed for barbershops, featuring a Telegram bot interface and Django REST API backend.

## 🌟 Features

### For Barbers (Telegram Bot)
- **Easy Registration**: Quick sign-up with name, phone number, and barbershop details
- **Towel Tracking**: Real-time view of current towel count and value
- **Transaction History**: Complete history of all towel transactions
- **Instant Notifications**: Receive detailed notifications for every towel operation

### For Admins (Telegram Bot)
- **Barber Management**: Complete overview and management of all barbers
- **Dynamic Pricing**: Individual towel pricing per barber with easy updates
- **Inventory Control**: Monitor stock levels and towel usage
- **Advanced Reporting**: Generate detailed reports by period (daily, weekly, monthly, all-time)
- **Real-time Operations**: Instant towel give/take operations with automatic notifications

### Backend (Django REST API)
- **RESTful API**: Full CRUD operations for all entities
- **Admin Dashboard**: Django admin interface for comprehensive data management
- **Reporting System**: Flexible reporting endpoints with period-based filtering
- **Data Security**: Robust authentication and data validation

## 🛠 Technology Stack

### Backend
- **Django 4.2.7**: High-level Python web framework
- **Django REST Framework**: Powerful API development toolkit
- **SQLite**: Lightweight database (easily upgradable to PostgreSQL)
- **CORS Headers**: Cross-origin resource sharing support

### Telegram Bot
- **pyTelegramBotAPI 4.15.2**: Feature-rich Telegram bot framework
- **SOCKS5 Proxy Support**: Built-in proxy configuration for restricted networks
- **Interactive Keyboards**: Dynamic inline and reply keyboards
- **Real-time Communication**: Instant messaging and callback handling

## 📋 Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [BotFather](https://t.me/BotFather))
- Django superuser account for API access

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/BotirBakhtiyarov/RentingTowel-TelegramBot.git
cd RentingTowel-TelegramBot
```

### 2. Backend Setup

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser
```bash
python manage.py createsuperuser
```

#### Start Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### 3. Telegram Bot Setup

#### Navigate to Bot Directory
```bash
cd ../bot
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the bot directory:

```env
BOT_TOKEN=your_telegram_bot_token_here
API_URL=http://localhost:8000/api
ADMIN_IDS=123456789,987654321
DJANGO_USERNAME=admin
DJANGO_PASSWORD=your_password
```

#### Start the Bot
```bash
python bot.py
```

## ⚙ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot API token | Required |
| `API_URL` | Django backend API URL | `http://localhost:8000/api` |
| `ADMIN_IDS` | Comma-separated Telegram user IDs for admin access | Required |
| `DJANGO_USERNAME` | Django admin username | `admin` |
| `DJANGO_PASSWORD` | Django admin password | Required |

### Proxy Configuration (Optional)
For environments requiring proxy access, configure SOCKS5 proxy in `bot.py`:

```python
SOCKS_PROXY_HOST = '127.0.0.1'
SOCKS_PROXY_PORT = 10808
```

## 📱 Usage

### For Barbers

1. **Start the Bot**: Send `/start` to your Telegram bot
2. **Registration**: Complete the registration process with your details
3. **View Towels**: Check current towel count and value
4. **Transaction History**: Review all past operations
5. **Receive Notifications**: Get instant updates for all towel activities

### For Admins

1. **Access Admin Features**: Use the admin menu in Telegram
2. **Manage Barbers**: View and manage all registered barbers
3. **Towel Operations**: Give or take towels from barbers
4. **Price Management**: Update individual barber towel prices
5. **Generate Reports**: Create detailed financial and inventory reports

## 🔌 API Endpoints

### Barbers
- `GET /api/barbers/` - List all barbers
- `POST /api/barbers/` - Create new barber
- `GET /api/barbers/{id}/` - Retrieve specific barber
- `PATCH /api/barbers/{id}/` - Update barber details
- `POST /api/barbers/{id}/update_towel_price/` - Update towel price

### Transactions
- `GET /api/transactions/` - List all transactions
- `POST /api/transactions/` - Create new transaction

### Inventory
- `GET /api/inventory/` - Get current inventory status
- `POST /api/inventory/initialize/` - Initialize inventory

### Reports
- `GET /api/reports/?period={period}` - Generate reports
  - Periods: `today`, `week`, `month`, `all`

## 🗂 Project Structure

```
RentingTowel-TelegramBot/
├── backend/                 # Django REST API
│   ├── sochiq_app/         # Main application
│   │   ├── models.py       # Database models
│   │   ├── views.py        # API views
│   │   ├── serializers.py  # Data serializers
│   │   └── urls.py         # URL routing
│   ├── backend/            # Project settings
│   └── manage.py
├── bot/                    # Telegram bot
│   ├── handlers/           # Message handlers
│   │   ├── admin_handlers.py
│   │   ├── barber_handlers.py
│   │   └── register_handlers.py
│   ├── utils/              # Utilities
│   │   ├── api_client.py
│   │   └── keyboards.py
│   ├── config.py          # Configuration file  
│   └── bot.py             # Main bot file
└── requirements.txt       # Python dependencies
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot Connection Issues**
   - Verify BOT_TOKEN is correct
   - Check internet connection and proxy settings
   - Ensure Telegram is not blocked in your region

2. **API Connection Problems**
   - Confirm Django server is running
   - Verify API_URL in environment variables
   - Check Django admin credentials

3. **Database Issues**
   - Run migrations: `python manage.py migrate`
   - Create superuser if needed
   - Check database file permissions

### Logs and Debugging

- Backend logs are displayed in the Django server console
- Bot logs show detailed error messages and API interactions
- Enable debug mode in Django settings for detailed error information

## 🤝 Contributing

We welcome contributions! Please feel free to submit pull requests, report bugs, or suggest new features.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation

## 🚀 Deployment

### Production Considerations

- Use PostgreSQL instead of SQLite for production
- Set `DEBUG = False` in Django settings
- Configure proper CORS settings
- Use environment variables for all sensitive data
- Set up proper logging and monitoring
- Consider using Docker for containerization

---

**Built with ❤️ for the barber community**
