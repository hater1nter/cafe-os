# Café OS — Premium Telegram Ordering Platform

A production-ready SaaS platform for coffee shops and restaurants to receive orders directly in Telegram with real-time tracking, multi-tenant support, and Russian payment provider integration.

## Technology Stack

**Backend**:
- Python 3.12
- FastAPI 0.104+
- SQLAlchemy 2.0 + Alembic
- PostgreSQL 15
- Redis 7
- aiogram 3.x (Telegram Bot)

**Admin Dashboard**:
- Next.js 14 (coming in Phase 1E)
- React 18
- TypeScript
- Tailwind CSS

**Infrastructure**:
- Docker & Docker Compose
- Nginx reverse proxy
- Self-hosted VPS deployment

## Features

- ✅ Multi-tenant SaaS architecture
- ✅ Real-time order tracking with HTML Bubbles
- ✅ Telegram Bot integration
- ✅ Russian payment providers (YandexKassa, YuKassa, SberPay)
- ✅ Live barista queue
- ✅ Loyalty system
- ✅ Admin dashboard
- ✅ Menu management
- ✅ Staff management

## Project Structure

```
café-os/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── config.py       # Settings
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── dependencies.py # Auth & DI
│   │   ├── api/
│   │   │   ├── customer.py    # Customer endpoints
│   │   │   ├── admin.py       # Admin endpoints
│   │   │   ├── barista.py     # Barista endpoints
│   │   │   ├── telegram_webhook.py
│   │   │   └── payment_webhook.py
│   │   └── services/
│   │       └── payment_provider.py  # Payment abstraction
│   ├── alembic/
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── admin-dashboard/        # Next.js admin panel (Phase 1E)
├── html-bubbles/          # Telegram HTML widgets (Phase 1D)
├── docker-compose.yml
├── nginx.conf
├── .env.example
└── README.md
```

## Setup & Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- Git

### Quick Start with Docker

1. **Clone repository**:
```bash
git clone <repo-url>
cd cafe-os
```

2. **Create environment file**:
```bash
cp .env.example .env
# Edit .env and add your Telegram bot token and payment provider credentials
```

3. **Start services**:
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Nginx reverse proxy (port 80)

4. **Run database migrations**:
```bash
docker-compose exec backend alembic upgrade head
```

5. **Create demo café**:
```bash
docker-compose exec backend python -c "
from app.main import app
from app.database import engine, Base
import asyncio

async def init_demo():
    # TODO: Implement demo data creation
    pass

asyncio.run(init_demo())
"
```

### Local Development

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

3. **Set environment variables**:
```bash
cp ../.env.example ../.env
```

4. **Run database migrations**:
```bash
cd backend
alembic upgrade head
```

5. **Start FastAPI server**:
```bash
uvicorn app.main:app --reload
```

Server will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

## API Endpoints

### Customer API

```
GET    /api/v1/customer/menu                    # Get menu
POST   /api/v1/customer/orders                  # Create order
GET    /api/v1/customer/orders/{order_id}      # Get order details
GET    /api/v1/customer/orders                 # Get user's orders
PATCH  /api/v1/customer/orders/{order_id}/cancel
GET    /api/v1/customer/user/profile           # Get user profile
GET    /api/v1/customer/user/loyalty-card      # Get loyalty info
```

### Admin API

```
GET    /api/v1/admin/dashboard                 # Dashboard stats
GET    /api/v1/admin/orders                    # List orders
PATCH  /api/v1/admin/orders/{order_id}/status  # Update order status
GET    /api/v1/admin/menu/products             # List products
POST   /api/v1/admin/menu/products             # Create product
GET    /api/v1/admin/staff                     # List staff
```

### Barista API

```
GET    /api/v1/barista/queue                   # Get queue
PATCH  /api/v1/barista/order/{order_id}/start  # Start preparing
PATCH  /api/v1/barista/order/{order_id}/ready  # Mark as ready
PATCH  /api/v1/barista/order/{order_id}/complete
```

## Payment Providers

Three Russian payment systems supported:

1. **YandexKassa** (Яндекс.Касса)
   - Most popular in Russia
   - Multiple payment methods
   - Setup: Add `YANDEX_KASSA_SHOP_ID` and `YANDEX_KASSA_SECRET_KEY` to `.env`

2. **YuKassa** (ЮKassa)
   - Modern platform
   - Good API
   - Setup: Add `YUKASSA_MERCHANT_ID` and `YUKASSA_SECRET_KEY` to `.env`

3. **SberPay**
   - Direct Sberbank integration
   - Setup: Add `SBERPAY_MERCHANT_ID` and `SBERPAY_SECRET_KEY` to `.env`

## Development Phases

### Phase 1A: ✅ Project Setup (Days 1-2)
- ✅ Docker Compose
- ✅ FastAPI scaffold
- ✅ Database schema
- ✅ Environment config

### Phase 1B: ✅ Backend Core (Days 3-5)
- ✅ SQLAlchemy models
- ✅ Alembic migrations
- ✅ JWT auth
- ✅ Customer API (menu, orders)
- 🔄 Order service logic (in progress)

### Phase 1C: 🔄 Payment Integration (Days 5-6)
- ✅ Payment provider abstraction
- ✅ YandexKassa implementation
- ✅ YuKassa implementation
- ✅ SberPay implementation
- 🔲 Webhook handlers
- 🔲 Payment status tracking

### Phase 1D: 🔲 Telegram Bot (Days 7-9)
- 🔲 Aiogram bot setup
- 🔲 Webhook handler
- 🔲 Menu delivery
- 🔲 Order tracking widget
- 🔲 HTML Bubbles widgets

### Phase 1E: 🔲 Admin Dashboard (Days 10-12)
- 🔲 Next.js setup
- 🔲 Admin auth
- 🔲 Dashboard UI
- 🔲 Order management
- 🔲 Barista interface

## Database Schema

### Core Tables

- **organizations**: Multi-tenant support
- **branches**: Multiple locations per café
- **users**: Customer accounts (Telegram-based)
- **products**: Menu items
- **categories**: Menu categories
- **modifiers**: Product customizations
- **orders**: Customer orders
- **order_status_history**: Order timeline
- **staff**: Employee management
- **loyalty_accounts**: Loyalty program
- **loyalty_transactions**: Points transactions

## Configuration

All configuration is managed via environment variables in `.env`:

```env
# Core
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@localhost/cafe_os

# Redis
REDIS_URL=redis://localhost:6379

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Payment providers
YANDEX_KASSA_SHOP_ID=...
YANDEX_KASSA_SECRET_KEY=...

YUKASSA_MERCHANT_ID=...
YUKASSA_SECRET_KEY=...

SBERPAY_MERCHANT_ID=...
SBERPAY_SECRET_KEY=...

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### API Documentation

OpenAPI/Swagger docs available at: `http://localhost:8000/docs`

### Integration Tests

```bash
# Coming in Phase 1F
pytest tests/
```

## Deployment

### Production Deployment

1. **Configure environment** on VPS:
```bash
# Copy docker-compose.yml and .env to VPS
# Update .env with production values
# Enable SSL with Let's Encrypt
```

2. **Start services**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

3. **Run migrations**:
```bash
docker-compose exec backend alembic upgrade head
```

4. **Monitor**:
```bash
docker-compose logs -f backend
docker-compose ps
```

## Troubleshooting

### Database Connection Error
```
Check PostgreSQL container status:
docker-compose ps postgres

Check connection string in .env
```

### Port Already in Use
```
Change ports in docker-compose.yml or stop conflicting services:
lsof -i :8000  # Find process using port 8000
kill -9 <PID>
```

### Alembic Migration Failed
```
Check database exists:
docker-compose exec postgres psql -U cafe_os -l

Reset migrations (dev only):
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

## Team

Built by:
- Principal Software Architect
- Senior Full-Stack Engineer
- Telegram Bot API Specialist
- UI/UX Designer
- Backend Engineer
- DevOps Engineer

## License

Proprietary - Café OS Team

## Support

For issues or questions, please contact: support@cafe-os.local

---

**Status**: In Development (MVP - Phase 1)

**Next Steps**: 
- Phase 1C: Complete payment webhook handlers
- Phase 1D: Implement Telegram bot and HTML Bubbles
- Phase 1E: Build admin dashboard
