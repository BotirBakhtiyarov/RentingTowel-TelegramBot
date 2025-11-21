# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-11-21

### Removed
- **Django Backend**: Completely removed Django REST API backend
- **Barbershop Name**: Removed barbershop name field from user registration and display
- **Prices**: Removed towel price functionality (no pricing tracking)
- **API Client**: Removed Django API client dependency

### Added
- **Direct Database Integration**: Telegram bot now uses SQLAlchemy ORM directly
- **Database Support**: Added support for both SQLite and PostgreSQL based on configuration
- **Admin Message Feature**: Admins can now send messages to all users or selected users via bot
- **DeepSeek AI Integration**: AI-powered report generation for admins using DeepSeek API
- **Environment Configuration**: All configuration moved to `.env` file for easy deployment
- **Docker Support**: Added Dockerfile and docker-compose.yml for easy deployment
- **Database Service Layer**: New service layer for database operations replacing API client

### Changed
- **Architecture**: Standalone telegram bot (no external backend dependency)
- **User Model**: Simplified user model (removed barbershop_name and towel_price fields)
- **Transaction Model**: Simplified transaction model (removed price calculations)
- **Handler Updates**: All handlers updated to use database service instead of API client
- **Registration Flow**: Simplified registration (removed barbershop name step)

### Configuration
- Database type can be selected via `DB_STYLE` in `.env` (sqlite or postgres)
- All environment variables moved to `.env` file
- Proxy configuration is now optional and configurable via `.env`

### Technical
- **Database**: SQLAlchemy ORM with support for SQLite and PostgreSQL
- **Dependencies**: Removed Django and related packages, added SQLAlchemy and psycopg2-binary
- **Database Connection**: Dynamic database connection based on `DB_STYLE` environment variable

## [1.0.0] - Previous Version

### Features
- Django REST API backend
- Telegram bot with API integration
- Barber management system
- Towel rental tracking
- Price management
- Transaction history
- Reports and inventory management

