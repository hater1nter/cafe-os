# ✅ Railway Deployment Checklist

**Quick reference for deploying Café OS to Railway**

---

## Pre-Deployment (Do These First)

- [ ] All code committed to `main` branch
- [ ] `.gitignore` includes `.env` (secrets won't leak)
- [ ] `Dockerfile` at root level exists
- [ ] `backend/requirements.txt` is complete
- [ ] Local Docker build works: `docker build -t cafe-os .`
- [ ] Telegram bot token is valid and working

---

## Railway Setup (5 minutes)

### Account & Repository
- [ ] Create Railway account at railway.app
- [ ] Connect GitHub (authorize Railway access)
- [ ] Select `cafe-os` repository
- [ ] Select `main` branch

### Services
- [ ] Backend deployed (auto-detected from Dockerfile)
- [ ] PostgreSQL service added
- [ ] Redis service added
- [ ] All 3 services show as "Running" (🟢)

---

## Configuration (10 minutes)

### Environment Variables (in backend service)

**Auto-injected by Railway:**
- [ ] `DATABASE_URL` (from PostgreSQL service)
- [ ] `REDIS_URL` (from Redis service)

**Add manually:**
- [ ] `ENVIRONMENT=production`
- [ ] `SECRET_KEY=<32+ char random string>`
- [ ] `TELEGRAM_BOT_TOKEN=<your-token>`
- [ ] `CORS_ORIGINS=https://your-app.railway.app`
- [ ] `LOG_LEVEL=INFO`

**Optional (payment providers):**
- [ ] `YANDEX_KASSA_SHOP_ID` (if using)
- [ ] `YANDEX_KASSA_SECRET_KEY` (if using)
- [ ] `YUKASSA_MERCHANT_ID` (if using)
- [ ] `YUKASSA_SECRET_KEY` (if using)
- [ ] `SBERPAY_MERCHANT_ID` (if using)
- [ ] `SBERPAY_SECRET_KEY` (if using)

### Deployment Settings
- [ ] Port set to `8000`
- [ ] Health check enabled at `/health`
- [ ] Health check interval: `30s`

---

## First Deployment (Watch Logs)

- [ ] Code builds successfully
- [ ] No Docker build errors
- [ ] PostgreSQL service connects
- [ ] Redis service connects
- [ ] Alembic migrations run: `alembic upgrade head`
- [ ] Demo data loads: `python init_demo_data.py`
- [ ] Uvicorn starts: `listening on 0.0.0.0:8000`
- [ ] Health check passes

---

## Verify Deployment (5 minutes)

### Health Check
```bash
curl https://your-app.railway.app/health
```
Expected: `{"status":"ok","environment":"production"}`

### API Docs
- [ ] Swagger UI loads: `https://your-app.railway.app/docs`
- [ ] Can see all endpoints

### Database
- [ ] PostgreSQL service shows data
- [ ] Can connect to database
- [ ] Tables created (organizations, orders, etc.)

### Redis
- [ ] Redis service is running
- [ ] Can connect from backend logs

---

## Telegram Bot Test (2 minutes)

- [ ] Find your bot in Telegram
- [ ] Send `/start`
- [ ] See greeting message
- [ ] Can browse menu
- [ ] Can view order history
- [ ] Bot responses are instant

---

## Production Monitoring (Ongoing)

### Daily
- [ ] Check logs for errors
- [ ] Monitor health check status
- [ ] Verify bot is responding

### Weekly
- [ ] Review performance metrics
- [ ] Check database backup status
- [ ] Monitor costs

### Monthly
- [ ] Update dependencies
- [ ] Test disaster recovery
- [ ] Review and rotate secrets

---

## Troubleshooting Guide

### Service Shows "Crashed" 🔴

**Step 1: Check Logs**
```
Backend service → Logs → look for ERROR
```

**Step 2: Common Issues**
- `DATABASE_URL not set` → Add to variables
- `Connection refused` → PostgreSQL not ready
- `ModuleNotFoundError` → requirements.txt missing
- `AlembicError` → Database schema issue

**Step 3: Restart**
```
Service menu → Redeploy
```

### Alembic Migration Failed

**Check:**
1. `DATABASE_URL` is set correctly
2. Format: `postgresql://user:pass@host:port/db`
3. Database exists and is accessible

**Restart Migration:**
```
Service → Settings → Redeploy
```

### Bot Not Responding

**Verify:**
1. `TELEGRAM_BOT_TOKEN` is set in variables
2. Token is correct format: `NUMBERS:LETTERS-_`
3. No trailing spaces or quotes
4. Bot not running locally elsewhere

**Restart Bot:**
```
Backend service → Redeploy
```

### Out of Memory

**Solution:**
1. Backend service → Settings
2. Increase "Memory Limit" to 1GB
3. Restart service

### Slow Response Times

**Check:**
1. Backend metrics → Response time
2. Database queries → Are they optimized?
3. Network latency → Check logs
4. Scale horizontally → Add replicas

---

## After Successful Deployment

### Custom Domain (Optional)
- [ ] Backend service → Settings → Add Domain
- [ ] Point DNS to Railway
- [ ] SSL auto-configured (Let's Encrypt)

### Admin Dashboard (Optional)
- [ ] Deploy admin-dashboard separately
- [ ] Connect to same backend
- [ ] Configure CORS

### Backups (Important!)
- [ ] PostgreSQL service → Settings → Enable backups
- [ ] Test restore process
- [ ] Document backup location

### Monitoring (Recommended)
- [ ] Set up alerts for errors
- [ ] Monitor resource usage
- [ ] Create runbook for common issues

---

## Emergency Contacts

| Issue | Action |
|-------|--------|
| Service down | Check Railway dashboard → Logs |
| Database corrupted | Restore from backup (PostgreSQL → Backups) |
| Bot token leaked | Create new token in Telegram BotFather |
| High costs | Check metrics → Scale down resources |

---

## Success Indicators ✅

Your deployment is successful when:

1. ✅ All 3 services show "Running" (🟢)
2. ✅ API responds to `/health` endpoint
3. ✅ Swagger docs load at `/docs`
4. ✅ Telegram bot responds to `/start`
5. ✅ Can create orders through bot
6. ✅ Database contains data
7. ✅ Logs show no errors
8. ✅ Health check passes consistently

---

## Next Steps

1. **Monitor**: Watch logs for 24 hours
2. **Test**: Have team test the bot
3. **Configure**: Set up custom domain
4. **Optimize**: Monitor performance metrics
5. **Scale**: Add more replicas if needed
6. **Backup**: Verify backups are working

---

## Quick Links

- Railway Dashboard: https://railway.app/dashboard
- Project Logs: https://railway.app/dashboard/project/YOUR-PROJECT-ID
- API Docs: https://your-app.railway.app/docs
- Telegram BotFather: https://t.me/BotFather

---

**Deployment Time**: ~5-10 minutes
**Monitoring Time**: Ongoing
**Status**: Ready to deploy! 🚀
