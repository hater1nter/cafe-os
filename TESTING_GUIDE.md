# 🚀 Café OS — Complete Setup & Testing Guide

Production-ready Telegram ordering platform for coffee shops. Full stack ready to deploy.

## ✅ Project Status

**Phase 1A-1B**: ✅ Complete (Backend infrastructure, database, API)
**Phase 1C**: ✅ Complete (Payment integration - YandexKassa, YuKassa, SberPay)
**Phase 1D**: ✅ Complete (Telegram bot, Live tracking HTML Bubble)
**Phase 1E**: ✅ Complete (Admin dashboard skeleton - Next.js)
**Phase 1F**: 🔄 Testing & Validation

---

## 🏗️ Architecture Overview

```
Telegram Bot (aiogram 3.x)
         ↓
┌─────────────────────────┐
│  FastAPI Backend        │  ← Payment Webhooks (3 providers)
│  - Customer API         │  ← Order Management
│  - Admin API            │  ← Barista Queue
│  - Barista API          │
└──────────┬──────────────┘
           ↓ SQL
    PostgreSQL 15 + Alembic
           ↑ Cache
        Redis 7
           ↑
       Nginx (Port 80)
           ↑
   Admin Dashboard (Next.js 14)
```

---

## 📦 What's Included

### Backend (FastAPI)
- ✅ Multi-tenant SQLAlchemy models
- ✅ JWT + Telegram auth
- ✅ Payment provider abstraction (3 providers)
- ✅ Aiogram bot with webhooks
- ✅ Order lifecycle management
- ✅ Live tracking system
- ✅ Loyalty program

### Database
- ✅ PostgreSQL schema (11 tables)
- ✅ Alembic migrations
- ✅ Indexes & constraints
- ✅ Multi-tenant row isolation

### Frontend
- ✅ HTML Bubble tracking widget (self-contained, <12KB)
- ✅ Next.js admin dashboard skeleton
- ✅ Responsive design (Tailwind CSS)

### Payment Integration
- ✅ YandexKassa provider
- ✅ YuKassa provider
- ✅ SberPay provider
- ✅ Webhook handlers
- ✅ Test mode support

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12 (local dev)
- Node.js 18+ (admin dashboard)
- Git

### Option 1: Docker (Recommended)

```bash
# 1. Clone & navigate
git clone <repo>
cd cafe-os

# 2. Create .env
cp .env.example .env

# 3. Add your Telegram bot token
nano .env
# Set: TELEGRAM_BOT_TOKEN=your_token_here

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec backend alembic upgrade head

# 6. Initialize demo data
docker-compose exec backend python init_demo_data.py

# 7. Verify
curl http://localhost:8000/health
```

**Services available**:
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### Option 2: Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup database
export DATABASE_URL=postgresql://cafe_os:changeme@localhost/cafe_os_dev
alembic upgrade head

# Run server
uvicorn app.main:app --reload

# In another terminal - Admin Dashboard
cd ../admin-dashboard
npm install
npm run dev  # http://localhost:3000
```

---

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health

# Response:
# {"status":"ok","version":"0.1.0","environment":"development"}
```

### API Testing with cURL

```bash
# Get menu
curl "http://localhost:8000/api/v1/customer/menu?organization_id=00000000-0000-0000-0000-000000000001"

# Create order
curl -X POST http://localhost:8000/api/v1/customer/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_type": "takeaway",
    "branch_id": "00000000-0000-0000-0000-000000000002",
    "items": [{"product_id": "uuid", "quantity": 1, "modifiers": []}]
  }' \
  -G -d "telegram_id=test_user" -d "organization_id=00000000-0000-0000-0000-000000000001"

# Get order details
curl "http://localhost:8000/api/v1/customer/orders/{order_id}?telegram_id=test_user&organization_id=00000000-0000-0000-0000-000000000001"

# Get tracking widget HTML
curl "http://localhost:8000/api/v1/customer/orders/{order_id}/tracking-widget?telegram_id=test_user&organization_id=00000000-0000-0000-0000-000000000001"

# Admin dashboard
curl "http://localhost:8000/api/v1/admin/dashboard?organization_id=00000000-0000-0000-0000-000000000001"

# Update order status
curl -X PATCH "http://localhost:8000/api/v1/admin/orders/{order_id}/status?organization_id=00000000-0000-0000-0000-000000000001&new_status=preparing"
```

### Integration Tests

```bash
cd backend

# Install test deps
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/test_integration.py -v

# Run specific test
pytest tests/test_integration.py::test_create_order -v
```

### Manual Flow Test

```bash
# 1. Start backend
docker-compose up -d

# 2. Initialize demo
docker-compose exec backend python init_demo_data.py

# 3. Get menu
MENU=$(curl -s "http://localhost:8000/api/v1/customer/menu?organization_id=00000000-0000-0000-0000-000000000001")
echo $MENU | python -m json.tool

# 4. Create order
ORDER=$(curl -s -X POST http://localhost:8000/api/v1/customer/orders \
  -H "Content-Type: application/json" \
  -d '{
    "order_type": "takeaway",
    "branch_id": "00000000-0000-0000-0000-000000000002",
    "items": [{"product_id": "00000000-0000-0000-0000-000000000010", "quantity": 1, "modifiers": []}]
  }' \
  -G -d "telegram_id=demo_user_1" -d "organization_id=00000000-0000-0000-0000-000000000001")
ORDER_ID=$(echo $ORDER | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "Created order: $ORDER_ID"

# 5. Get tracking widget
curl -s "http://localhost:8000/api/v1/customer/orders/$ORDER_ID/tracking-widget?telegram_id=demo_user_1&organization_id=00000000-0000-0000-0000-000000000001" | python -m json.tool | head -20

# 6. Update status (admin)
curl -s -X PATCH "http://localhost:8000/api/v1/admin/orders/$ORDER_ID/status?organization_id=00000000-0000-0000-0000-000000000001&new_status=confirmed" | python -m json.tool

# 7. Check dashboard
curl -s "http://localhost:8000/api/v1/admin/dashboard?organization_id=00000000-0000-0000-0000-000000000001" | python -m json.tool
```

---

## 🔑 Configuration

All settings via `.env`:

```env
# Core
ENVIRONMENT=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://cafe_os:changeme@localhost/cafe_os_dev

# Redis
REDIS_URL=redis://localhost:6379

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token

# Payment Providers (Test Mode by Default)
YANDEX_KASSA_SHOP_ID=test_shop_id
YANDEX_KASSA_SECRET_KEY=test_secret_key

YUKASSA_MERCHANT_ID=test_merchant_id
YUKASSA_SECRET_KEY=test_secret_key

SBERPAY_MERCHANT_ID=test_merchant_id
SBERPAY_SECRET_KEY=test_secret_key

# Admin
ADMIN_EMAIL=admin@cafe-os.local
ADMIN_PASSWORD=changeme
```

---

## 📊 API Endpoints

### Customer Endpoints
```
GET    /api/v1/customer/menu                           # Menu
POST   /api/v1/customer/orders                         # Create order
GET    /api/v1/customer/orders/{order_id}             # Order details
GET    /api/v1/customer/orders/{order_id}/tracking-widget  # HTML widget
GET    /api/v1/customer/orders                         # Order history
PATCH  /api/v1/customer/orders/{order_id}/cancel      # Cancel
POST   /api/v1/customer/orders/{order_id}/checkout    # Payment
GET    /api/v1/customer/user/profile                  # Profile
GET    /api/v1/customer/user/loyalty-card             # Loyalty
```

### Admin Endpoints
```
GET    /api/v1/admin/dashboard                        # Dashboard stats
GET    /api/v1/admin/orders                           # List orders
PATCH  /api/v1/admin/orders/{order_id}/status        # Update status
GET    /api/v1/admin/menu/products                    # Menu
POST   /api/v1/admin/menu/products                    # Create product
GET    /api/v1/admin/staff                            # Staff list
```

### Barista Endpoints
```
GET    /api/v1/barista/queue                          # Queue
PATCH  /api/v1/barista/order/{order_id}/start        # Start
PATCH  /api/v1/barista/order/{order_id}/ready        # Ready
PATCH  /api/v1/barista/order/{order_id}/complete     # Complete
```

### Payment Webhooks
```
POST   /api/v1/payments/webhook/yandex_kassa         # YandexKassa
POST   /api/v1/payments/webhook/yukassa              # YuKassa
POST   /api/v1/payments/webhook/sberpay              # SberPay
```

### Telegram
```
POST   /api/v1/telegram/webhook                       # Bot webhook
GET    /api/v1/telegram/bot/info                      # Bot info
POST   /api/v1/telegram/bot/set-webhook              # Set webhook
GET    /api/v1/telegram/bot/webhook-info             # Webhook status
```

---

## 🗄️ Database Schema

```
organizations
├── branches
├── users
├── products
│   └── modifiers
├── categories
├── orders
│   └── order_status_history
├── loyalty_accounts
│   └── loyalty_transactions
└── staff
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error
```bash
# Check PostgreSQL running
docker-compose ps postgres

# Check connection string in .env
# Format: postgresql://user:pass@host:port/db
```

### Bot Not Responding
```bash
# Check token in .env
# Verify webhook is set
curl "http://localhost:8000/api/v1/telegram/bot/webhook-info"

# Restart bot
docker-compose restart backend
```

### Migration Issues
```bash
# Reset (dev only!)
docker-compose exec backend alembic downgrade base

# Re-apply
docker-compose exec backend alembic upgrade head

# Check status
docker-compose exec backend alembic current
```

---

## 📱 Testing with Telegram

1. **Create bot** on @BotFather → Get token
2. **Set webhook** (production):
   ```bash
   curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
     -F "url=https://yourdomain.com/api/v1/telegram/webhook"
   ```
3. **Test locally** (ngrok tunnel):
   ```bash
   ngrok http 8000
   # Set webhook to: https://your-ngrok-url/api/v1/telegram/webhook
   ```
4. **Send /start** to bot
5. **Test flow**: /menu → Select → Checkout

---

## 🚢 Production Deployment

### VPS Setup (Ubuntu 22.04)

```bash
# 1. SSH to VPS
ssh user@your-vps-ip

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Clone repo
git clone <repo>
cd cafe-os

# 4. Setup production .env
cp .env.example .env
# Edit with production values, real payment credentials

# 5. Setup SSL (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d yourdomain.com

# 6. Update nginx.conf with SSL paths

# 7. Start services
docker-compose -f docker-compose.yml up -d

# 8. Verify
curl https://yourdomain.com/health
```

### Environment Variables (Production)
```env
ENVIRONMENT=production
SECRET_KEY=<generate-strong-key>
TELEGRAM_WEBHOOK_URL=https://yourdomain.com/api/v1/telegram/webhook

# Real payment credentials
YANDEX_KASSA_SHOP_ID=<real-id>
YANDEX_KASSA_SECRET_KEY=<real-key>

# Database (managed service recommended)
DATABASE_URL=postgresql://user:pass@db-host:5432/cafe_os

# Redis (managed service)
REDIS_URL=redis://:password@redis-host:6379

# Logging
LOG_LEVEL=INFO
```

---

## 📈 Next Steps (Future Phases)

- [ ] WebSocket real-time updates for admin
- [ ] Full menu editor UI
- [ ] Advanced analytics & reporting
- [ ] Email & SMS notifications
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced loyalty mechanics
- [ ] Kitchen display system (KDS)
- [ ] Inventory management
- [ ] Marketing automation

---

## 📞 Support

Issues? Check:
1. Logs: `docker-compose logs -f backend`
2. API Docs: `http://localhost:8000/docs`
3. Database: `docker-compose exec postgres psql -U cafe_os -d cafe_os_dev`

---

**Status**: ✅ MVP Complete & Ready for Testing

**Built by**: Café OS Dev Team
**Stack**: Python + FastAPI + PostgreSQL + React + Telegram + 3 Payment Providers
**Time to Market**: 14 days
