# 🚀 Railway Deployment Guide for Café OS

Complete step-by-step guide to deploy Café OS to Railway with PostgreSQL, Redis, and auto-scaling.

---

## ✅ Pre-Deployment Checklist

- [ ] All code committed to main branch
- [ ] `.env` file with production secrets ready
- [ ] Railway account created (railway.app)
- [ ] GitHub repository connected
- [ ] Telegram bot token confirmed working

---

## Step 1: Create Railway Project

### 1.1 Go to Railway Dashboard
1. Visit [railway.app](https://railway.app)
2. Sign in with GitHub (recommended) or create account
3. Click **"New Project"**

### 1.2 Deploy from GitHub
1. Select **"Deploy from GitHub repo"**
2. Authorize Railway to access your GitHub
3. Select the `cafe-os` repository
4. Select the `main` branch
5. Click **"Deploy"**

**Railway will automatically:**
- Detect the `Dockerfile` in the root directory
- Build the Docker image
- Deploy the backend service

---

## Step 2: Add PostgreSQL Database

### 2.1 Add Database Service
1. In Railway dashboard, click **"+ Add Service"**
2. Select **"Database"** → **"PostgreSQL"**
3. Choose the latest stable version (15+)
4. Click **"Create"**

### 2.2 Configure PostgreSQL
Railway automatically:
- Creates a PostgreSQL instance
- Generates connection credentials
- Injects `DATABASE_URL` environment variable

**You'll see:**
```
SERVICE_NAME: postgres
DATABASE_URL: postgresql://user:pass@host:port/railway
```

---

## Step 3: Add Redis Cache

### 3.1 Add Redis Service
1. Click **"+ Add Service"**
2. Select **"Database"** → **"Redis"**
3. Choose the latest stable version (7+)
4. Click **"Create"**

### 3.2 Configure Redis
Railway automatically:
- Creates a Redis instance
- Generates connection credentials
- Injects `REDIS_URL` environment variable

**You'll see:**
```
SERVICE_NAME: redis
REDIS_URL: redis://user:pass@host:port
```

---

## Step 4: Configure Environment Variables

### 4.1 Access Variables Tab
1. In Railway dashboard, go to your **main service** (backend)
2. Click the **"Variables"** tab
3. Click **"Raw Editor"** or add individually

### 4.2 Add Production Variables

Add these variables (Railway auto-provides `DATABASE_URL` and `REDIS_URL`):

```env
# Core
ENVIRONMENT=production
SECRET_KEY=your-super-secret-production-key-min-32-chars
LOG_LEVEL=INFO

# Telegram
TELEGRAM_BOT_TOKEN=9193588742:AAGd-Cg7LoAlomutzWiV2u68wmHQ6K2I-Oo

# CORS (adjust to your domain)
CORS_ORIGINS=https://your-app.railway.app,https://admin.your-app.railway.app

# Payment Providers (optional - add only if using)
YANDEX_KASSA_SHOP_ID=your-shop-id
YANDEX_KASSA_SECRET_KEY=your-secret-key

YUKASSA_MERCHANT_ID=your-merchant-id
YUKASSA_SECRET_KEY=your-secret-key

SBERPAY_MERCHANT_ID=your-merchant-id
SBERPAY_SECRET_KEY=your-secret-key
```

### 4.3 Get Auto-Injected URLs

Click on **PostgreSQL service** → **"Variables"** to see:
```
DATABASE_URL=postgresql://...
```

Click on **Redis service** → **"Variables"** to see:
```
REDIS_URL=redis://...
```

**Copy these URLs into your backend service variables!**

---

## Step 5: Configure Deployment Settings

### 5.1 Port Configuration
1. Go to backend service → **"Settings"** tab
2. Find **"Port"** setting
3. Set to: **8000**

### 5.2 Health Check
1. In **"Settings"**, find **"Health Check"**
2. Set URL to: `/health`
3. Set Interval to: `30s`
4. Set Timeout to: `10s`

Railway will use this to:
- Detect service readiness
- Restart unhealthy instances
- Manage deployments smoothly

---

## Step 6: First Deployment

### 6.1 Trigger Deployment
1. Push code to `main` branch (if not already)
2. Railway auto-builds and deploys
3. Watch logs in real-time

### 6.2 Monitor Build Progress
1. Click backend service
2. View **"Logs"** tab
3. Watch for:
   ```
   ✓ Building Docker image
   ✓ Alembic migrations (alembic upgrade head)
   ✓ Demo data initialization
   ✓ Uvicorn server started
   ```

### 6.3 Check Deployment Status
```
🟢 Running = deployment successful
🔴 Crashed = check logs for errors
🟡 Building = in progress
```

---

## Step 7: Access Your Service

### 7.1 Get Service URL
1. Click backend service
2. In **"Environment"** tab, find **"Public URL"**
3. Example: `https://cafe-os-production.railway.app`

### 7.2 Test API
```bash
curl https://cafe-os-production.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "environment": "production",
  "timestamp": "2026-11-11T23:14:00Z"
}
```

### 7.3 Access Swagger Docs
```
https://cafe-os-production.railway.app/docs
```

---

## Step 8: Configure Domain (Optional)

### 8.1 Add Custom Domain
1. Go to backend service → **"Settings"**
2. Click **"+ Add Domain"**
3. Enter your domain (e.g., `api.cafe-os.com`)
4. Follow DNS instructions

### 8.2 SSL Certificate
Railway automatically:
- Generates SSL certificate (Let's Encrypt)
- Renews before expiration
- Redirects HTTP → HTTPS

---

## Step 9: Set Up Database Backups

### 9.1 PostgreSQL Backups
1. Click PostgreSQL service
2. Go to **"Settings"**
3. Enable **"Automatic Backups"**
4. Set retention to **30 days** minimum

### 9.2 Restore from Backup
1. Click PostgreSQL service
2. Go to **"Backups"** tab
3. Select backup and click **"Restore"**

---

## Step 10: Monitor Production

### 10.1 View Logs
```
Backend service → Logs → Filter by:
- ✅ Info: Normal operations
- ⚠️ Warning: Potential issues
- ❌ Error: Critical problems
```

### 10.2 Metrics
1. Click backend service
2. View **"Metrics"** tab:
   - CPU usage
   - Memory usage
   - Request count
   - Response time

### 10.3 Set Up Alerts (Optional)
1. Go to **"Project Settings"**
2. Find **"Alerts"**
3. Configure notifications for:
   - Deployment failures
   - High CPU/memory
   - Service crashes

---

## Troubleshooting

### Build Fails: "requirements.txt not found"
**Fix:**
```
Ensure backend/requirements.txt exists
Update Dockerfile:
  COPY backend/requirements.txt .
```

### Alembic Migration Fails
**Check:**
1. Database connection string in variables
2. `DATABASE_URL` format: `postgresql://user:pass@host:port/db`
3. Migrations exist in `backend/alembic/versions/`

**Logs to look for:**
```
docker-compose exec backend alembic upgrade head
```

### Bot Token Not Working
**Verify:**
1. Token format: `NUMBERS:LETTERS-_`
2. Correct in Railway variables
3. No extra spaces or quotes
4. Bot not already running elsewhere

### Out of Memory
**Solution:**
1. Click backend service → **"Settings"**
2. Increase **"Memory Limit"**
3. Restart service

### Slow Requests
**Check:**
1. PostgreSQL and Redis connection
2. Network latency between services
3. Database query optimization
4. View **"Metrics"** → Response Times

---

## Production Best Practices

### 1. Secrets Management
✅ **DO:**
- Store in Railway Variables
- Use strong SECRET_KEY (32+ characters)
- Rotate keys periodically

❌ **DON'T:**
- Commit `.env` to git
- Share tokens in code
- Use weak passwords

### 2. Database
✅ **DO:**
- Enable automatic backups
- Use strong database passwords
- Monitor connection pool
- Run migrations in deployment

❌ **DON'T:**
- Run migrations manually in production
- Share database credentials
- Use default passwords

### 3. Monitoring
✅ **DO:**
- Check logs daily
- Monitor resource usage
- Set up alerts
- Keep backups recent

❌ **DON'T:**
- Ignore error logs
- Let backups become outdated
- Deploy without testing

### 4. Deployments
✅ **DO:**
- Test locally first
- Use staging environment
- Deploy during low-traffic times
- Have rollback plan

❌ **DON'T:**
- Force-push to main
- Deploy untested changes
- Deploy during peak hours

---

## Auto-Deployment on Git Push

Railway automatically:
1. Detects push to `main` branch
2. Builds Docker image
3. Runs tests (if configured)
4. Deploys to production
5. Runs migrations
6. Restarts service

**Deployment takes:** ~3-5 minutes

---

## Scaling & Performance

### Scale Horizontally (Multiple Instances)
1. Backend service → **"Settings"**
2. Find **"Replica Count"**
3. Set to `2+` for redundancy
4. Railway auto-load-balances

### Increase Resources
1. Backend service → **"Settings"**
2. **"Memory Limit"**: 512MB → 1GB
3. **"CPU Limit"**: 0.5 → 1.0

---

## Backup & Disaster Recovery

### Daily Manual Backup
```bash
# From local machine
railway run pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql
```

### Restore from Backup
```bash
# In Railway PostgreSQL shell
railway connect postgres
psql < backup-20261111.sql
```

---

## Cost Estimation (Railway Pricing)

| Component | Tier | Monthly Cost |
|-----------|------|--------------|
| Backend (512MB) | Pay-as-you-go | ~$5-10 |
| PostgreSQL (10GB) | Fixed | ~$15 |
| Redis (1GB) | Fixed | ~$5 |
| **Total** | | ~$25-30/month |

*Prices vary based on region and usage*

---

## Next Steps

1. ✅ Connect GitHub repository
2. ✅ Add PostgreSQL & Redis
3. ✅ Configure environment variables
4. ✅ Deploy and monitor
5. 🔄 Set up admin dashboard (if needed)
6. 📊 Monitor performance metrics
7. 🔔 Set up alerts

---

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs
- **Telegram Bot API**: https://core.telegram.org/bots/api

---

## Production Deployment Complete! 🎉

Your Café OS is now live on Railway. Monitor the logs, test the endpoints, and enjoy the platform!

**Status**: ✅ PRODUCTION READY

**Next**: Connect your custom domain and configure payment providers for real transactions.
