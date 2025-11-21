# Towel Renting Service - Telegram Bot

A standalone Telegram bot for managing towel rentals with integrated database and AI-powered reporting.

![badge](https://img.shields.io/badge/License-MIT-yellow.svg)
![badge](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![badge](https://img.shields.io/badge/pyTelegramBotAPI-4.29.1-26A5E4?logo=telegram&logoColor=white)
![badge](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-green)

## 🌟 Features

### For Users
- **Easy Registration**: Quick sign-up with name and phone number
- **Towel Tracking**: Real-time view of current towel count
- **Transaction History**: Complete history of all towel transactions
- **Instant Notifications**: Receive detailed notifications for every towel operation

### For Admins
- **User Management**: Complete overview and management of all users
- **Towel Operations**: Give or take towels from users with automatic notifications
- **Inventory Control**: Monitor stock levels and towel usage
- **Advanced Reporting**: Generate detailed reports by period (daily, weekly, monthly, all-time)
- **AI-Powered Reports**: Get AI-generated insights about towel renting using DeepSeek AI
- **Message Broadcasting**: Send messages to all users or selected users via bot

## 🛠 Technology Stack

- **Telegram Bot**: pyTelegramBotAPI 4.29.1
- **Database**: SQLAlchemy ORM with SQLite or PostgreSQL support
- **AI Integration**: DeepSeek AI for intelligent report generation
- **Containerization**: Docker & Docker Compose support
- **Configuration**: Environment variables via `.env` file

## 📋 Prerequisites

- Python 3.11 or higher
- Telegram Bot Token (from [BotFather](https://t.me/BotFather))
- (Optional) PostgreSQL database for production
- (Optional) DeepSeek API key for AI reports

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/RentingTowel-TelegramBot.git
cd RentingTowel-TelegramBot
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` file:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Admin Configuration
ADMIN_IDS=123456789,987654321

# Database Configuration
# Options: sqlite or postgres
DB_STYLE=sqlite

# SQLite Configuration (if DB_STYLE=sqlite)
DB_PATH=towel_rental.db

# PostgreSQL Configuration (if DB_STYLE=postgres)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=towel_rental
DB_USER=postgres
DB_PASSWORD=postgres

# DeepSeek AI Configuration (Optional)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_URL=https://api.deepseek.com

# Proxy Configuration (Optional)
PROXY_ENABLED=false
PROXY_URL=socks5://127.0.0.1:10808
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Bot

#### Using Python directly:

```bash
python bot.py
```

#### Using Docker:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f bot
```

## ⚙ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Telegram Bot API token | - | ✅ Yes |
| `ADMIN_IDS` | Comma-separated Telegram user IDs | - | ✅ Yes |
| `DB_STYLE` | Database type: `sqlite` or `postgres` | `sqlite` | No |
| `DB_PATH` | SQLite database file path | `towel_rental.db` | No (if SQLite) |
| `DB_HOST` | PostgreSQL host | `localhost` | No (if PostgreSQL) |
| `DB_PORT` | PostgreSQL port | `5432` | No (if PostgreSQL) |
| `DB_NAME` | Database name | `towel_rental` | No (if PostgreSQL) |
| `DB_USER` | Database user | `postgres` | No (if PostgreSQL) |
| `DB_PASSWORD` | Database password | `postgres` | No (if PostgreSQL) |
| `DEEPSEEK_API_KEY` | DeepSeek AI API key | - | No (for AI reports) |
| `DEEPSEEK_API_URL` | DeepSeek API endpoint | `https://api.deepseek.com` | No |
| `PROXY_ENABLED` | Enable proxy | `false` | No |
| `PROXY_URL` | Proxy URL | `socks5://127.0.0.1:10808` | No |

### Database Configuration

#### SQLite (Default - Development)

Set in `.env`:
```env
DB_STYLE=sqlite
DB_PATH=towel_rental.db
```

#### PostgreSQL (Production)

Set in `.env`:
```env
DB_STYLE=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=towel_rental
DB_USER=postgres
DB_PASSWORD=your_password
```

## 📱 Usage

### For Users

1. **Start the Bot**: Send `/start` to your Telegram bot
2. **Registration**: Complete the registration process with your name and phone number
3. **View Towels**: Check current towel count
4. **Transaction History**: Review all past operations
5. **Receive Notifications**: Get instant updates for all towel activities

### For Admins

1. **Access Admin Features**: Your Telegram ID must be in `ADMIN_IDS` in `.env`
2. **Manage Users**: View and manage all registered users
3. **Towel Operations**: Give or take towels from users
4. **Generate Reports**: Create detailed financial and inventory reports
5. **AI Reports**: Get AI-powered insights using DeepSeek AI (requires API key)
6. **Send Messages**: Broadcast messages to all users or selected users

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Start all services (bot + PostgreSQL)
docker-compose up -d

# Stop services
docker-compose stop

# View logs
docker-compose logs -f bot

# Restart services
docker-compose restart
```

### Custom Docker Build

```bash
# Build image
docker build -t towel-bot .

# Run container
docker run -d \
  --name towel-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  towel-bot
```

## 🗂 Project Structure

```
RentingTowel-TelegramBot/
├── database/                # Database layer
│   ├── models.py           # SQLAlchemy models
│   ├── db.py               # Database connection
│   └── service.py          # Database service layer
├── handlers/                # Message handlers
│   ├── admin_handlers.py
│   ├── barber_handlers.py
│   └── register_handlers.py
├── utils/                   # Utilities
│   ├── ai_service.py       # DeepSeek AI integration
│   ├── keyboards.py        # Bot keyboards
│   └── helpers.py          # Helper functions
├── config.py                # Configuration
├── bot.py                   # Main bot file
├── .env.example             # Environment variables example
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── CHANGELOG.md             # Changelog
└── README.md                # This file
```

## 🔧 Development

### Database Migrations

The database is automatically initialized on first run. Tables are created automatically using SQLAlchemy.

### Adding New Features

1. Database models: Add to `bot/database/models.py`
2. Database operations: Add to `bot/database/service.py`
3. Bot handlers: Add to appropriate handler file in `bot/handlers/`
4. Utilities: Add to `bot/utils/`

## 🐛 Troubleshooting

### Common Issues

1. **Bot Connection Issues**
   - Verify `BOT_TOKEN` is correct
   - Check internet connection and proxy settings
   - Ensure Telegram is not blocked in your region

2. **Database Issues**
   - SQLite: Check file permissions
   - PostgreSQL: Verify connection credentials
   - Ensure `DB_STYLE` is set correctly in `.env`

3. **AI Reports Not Working**
   - Verify `DEEPSEEK_API_KEY` is set in `.env`
   - Check API key validity
   - Ensure internet connection is available

### Logs

- Bot logs are displayed in the console
- Enable debug mode for detailed error information
- Docker logs: `docker-compose logs -f bot`

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

## 🔄 Migration from Django Version

If you're migrating from the Django version (v1.x):

1. **Backup Data**: Export your data from Django admin
2. **Update Configuration**: Set up `.env` file with new configuration
3. **Database**: Choose SQLite or PostgreSQL in `DB_STYLE`
4. **Import Data**: Manually import data if needed (database structure changed)
5. **Remove Django**: Django backend is no longer needed

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

## 📞 Support

For support and questions:
- Open an issue on GitHub
- Check the documentation
- Review the CHANGELOG.md for version updates

---

**Built with ❤️ for efficient towel rental management**
