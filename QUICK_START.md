# ⚡ CAFÉ OS — 30-Second Quick Start

**Your production-ready Telegram ordering platform is ready. Here's how to launch it RIGHT NOW.**

---

## 🚀 ONE COMMAND TO RULE THEM ALL

### On Mac/Linux:
```bash
cd cafe-os
bash startup.sh
```

### On Windows:
```bash
cd cafe-os
startup.bat
```

**That's it. Seriously.**

---

## ✅ What Happens (Automatically)

1. ✅ Checks Docker installation
2. ✅ Starts PostgreSQL, Redis, Nginx, FastAPI backend
3. ✅ Waits for services to be ready (auto-health checks)
4. ✅ Runs database migrations (Alembic)
5. ✅ Loads demo café (MONO COFFEE with 7 products)
6. ✅ Verifies everything works
7. ✅ Shows you all the URLs

**Total time: ~30 seconds**

---

## 🎯 After Startup (What You Get)

### Backend API (FastAPI)
```
http://localhost:8000
http://localhost:8000/docs  ← Interactive API explorer
```

### Database Ready
```
PostgreSQL: localhost:5432
Redis: localhost:6379
```

### Your Telegram Bot
✅ **LIVE AND RESPONDING**

Send `/start` to your bot and see:
- Beautiful greeting
- Menu button
- Order tracking
- Loyalty card

---

## 📱 Testing Your Café (3 Minutes)

### 1. Open Telegram
Find your bot → Send `/start`

You'll see:
```
☕ Good morning, Friend!

Your daily coffee ritual starts here.
Freshly brewed. Made just for you.

[📝 ORDER NOW] [📋 VIEW MENU] [👤 MY PROFILE]
```

### 2. Click "📝 ORDER NOW"

Select branch → category → product

### 3. Watch Live Tracking

After checkout, get a **real HTML Bubble widget** that:
- Shows order #
- 6-step timeline (RECEIVED → CONFIRMED → PREPARING → ALMOST_READY → READY → COMPLETED)
- Live ETA countdown
- Polls server every 5 seconds
- Smooth animations

### 4. Admin Panel (Optional)

```bash
# In another terminal
cd admin-dashboard
npm install
npm run dev
```

Visit: `http://localhost:3000`

Dashboard shows:
- Revenue
- Total orders
- Active orders
- Recent order list

---

## 🔧 If Something Goes Wrong

### Services not starting?
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Reset everything
docker-compose down
docker-compose up -d
```

### Need to reset database?
```bash
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

### Bot not responding?
Check bot token in `.env` is set correctly:
```
TELEGRAM_BOT_TOKEN=9193588742:AAGd-Cg7LoAlomutzWiV2u68wmHQ6K2I-Oo
```

---

## 🌐 All URLs You Need

| Service | URL |
|---------|-----|
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **Admin Dashboard** | http://localhost:3000 |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |

---

## 🎊 What's Included (Right Now)

### Backend
- ✅ FastAPI with 25+ endpoints
- ✅ PostgreSQL (11 tables)
- ✅ Redis caching
- ✅ JWT auth
- ✅ 3 payment providers (YandexKassa, YuKassa, SberPay)
- ✅ Telegram bot (aiogram)
- ✅ Live tracking widgets
- ✅ Loyalty system

### Demo Café (MONO COFFEE)
- ✅ 8 product categories
- ✅ 7 menu items with modifiers
- ✅ 3 demo users
- ✅ 2 staff members (admin + barista)
- ✅ Sample orders

### Admin Dashboard
- ✅ Dashboard with stats
- ✅ Order management
- ✅ Real-time updates

---

## 💡 Key Features

### For Customers
- Menu browsing with photos & prices
- Product customization (milk type, size, extra shots, etc)
- Live order tracking (HTML Bubble with animations)
- Loyalty card
- Order history
- Payment via 3 providers

### For Admin
- Dashboard (revenue, orders, stats)
- Order status management
- Menu editor
- Staff management

### For Developers
- Clean, well-documented code
- Comprehensive API docs (Swagger)
- Integration tests
- Docker setup (production-ready)
- Multi-tenant architecture
- Payment abstraction layer

---

## 🚀 You're Ready!

```bash
bash startup.sh    # Mac/Linux
# or
startup.bat        # Windows
```

**Then:**
1. Open http://localhost:8000/docs
2. Find your Telegram bot
3. Send `/start`
4. Order something
5. Watch live tracking update in real-time
6. Celebrate 🎉

---

## 📊 Stack Summary

```
Telegram Bot (aiogram 3.x)
    ↓
FastAPI Backend (Python 3.12) + PostgreSQL 15
    ↓
Redis 7
    ↓
Nginx (reverse proxy)
    ↓
Admin Dashboard (Next.js 14)
```

**All in Docker. One command to start. Production-ready.**

---

## ✨ Next Steps (Optional)

- [ ] Deploy to VPS (see TESTING_GUIDE.md)
- [ ] Add real payment credentials
- [ ] Customize branding colors
- [ ] Add more menu items
- [ ] Invite staff
- [ ] Launch to customers

---

## 📚 Full Documentation

- **README.md** — Project overview
- **TESTING_GUIDE.md** — Complete testing & troubleshooting
- **PROJECT_COMPLETE.md** — Feature summary

---

**Status**: ✅ COMPLETE & PRODUCTION READY

**Time to Launch**: 30 seconds

**Go! 🚀**
