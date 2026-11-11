#!/bin/bash

# 🚀 Café OS — Complete Startup Script
# Everything you need to launch production-ready ordering platform

set -e

echo "🎯 Café OS - Full Stack Startup"
echo "================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo -e "${BLUE}[1/7] Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"
echo ""

# Step 2: Check Docker Compose
echo -e "${BLUE}[2/7] Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose ready${NC}"
echo ""

# Step 3: Verify .env file
echo -e "${BLUE}[3/7] Verifying .env configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found, creating from .env.example${NC}"
    cp .env.example .env
fi

if grep -q "your-telegram-bot-token-here" .env; then
    echo -e "${RED}❌ Please set TELEGRAM_BOT_TOKEN in .env${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Configuration ready${NC}"
echo ""

# Step 4: Start services
echo -e "${BLUE}[4/7] Starting Docker services...${NC}"
docker-compose up -d

# Wait for services
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 10

# Check if PostgreSQL is ready
echo -e "${BLUE}   Checking PostgreSQL...${NC}"
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U cafe_os &> /dev/null; then
        echo -e "${GREEN}   ✅ PostgreSQL ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ PostgreSQL failed to start${NC}"
        exit 1
    fi
    sleep 1
done

# Check if Redis is ready
echo -e "${BLUE}   Checking Redis...${NC}"
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        echo -e "${GREEN}   ✅ Redis ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Redis failed to start${NC}"
        exit 1
    fi
    sleep 1
done

# Check if Backend is ready
echo -e "${BLUE}   Checking Backend API...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}   ✅ Backend API ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend API failed to start${NC}"
        exit 1
    fi
    sleep 1
done

echo ""

# Step 5: Run migrations
echo -e "${BLUE}[5/7] Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head
echo -e "${GREEN}✅ Migrations complete${NC}"
echo ""

# Step 6: Initialize demo data
echo -e "${BLUE}[6/7] Initializing demo café (MONO COFFEE)...${NC}"
docker-compose exec -T backend python init_demo_data.py
echo -e "${GREEN}✅ Demo data loaded${NC}"
echo ""

# Step 7: Verify everything
echo -e "${BLUE}[7/7] Final verification...${NC}"

echo -e "${YELLOW}   Testing API...${NC}"
HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"ok"')
if [ -n "$HEALTH" ]; then
    echo -e "${GREEN}   ✅ API responding${NC}"
else
    echo -e "${RED}   ❌ API not responding${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Café OS is LIVE and READY!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📊 Services Available:${NC}"
echo -e "  🌐 Backend API:        ${YELLOW}http://localhost:8000${NC}"
echo -e "  📖 API Documentation:  ${YELLOW}http://localhost:8000/docs${NC}"
echo -e "  💼 Admin Dashboard:    ${YELLOW}http://localhost:3000${NC} (npm run dev after setup)"
echo -e "  🗄️  PostgreSQL:         ${YELLOW}localhost:5432${NC}"
echo -e "  💾 Redis:              ${YELLOW}localhost:6379${NC}"
echo ""
echo -e "${BLUE}🤖 Telegram Bot:${NC}"
echo -e "  Bot Token: ${YELLOW}$(grep TELEGRAM_BOT_TOKEN .env | cut -d= -f2 | head -c 30)...${NC}"
echo ""
echo -e "${BLUE}🧪 Quick Tests:${NC}"
echo ""
echo -e "  # Health check"
echo -e "  ${YELLOW}curl http://localhost:8000/health${NC}"
echo ""
echo -e "  # Get menu"
echo -e "  ${YELLOW}curl \"http://localhost:8000/api/v1/customer/menu?organization_id=00000000-0000-0000-0000-000000000001\"${NC}"
echo ""
echo -e "  # View logs"
echo -e "  ${YELLOW}docker-compose logs -f backend${NC}"
echo ""
echo -e "  # Stop services"
echo -e "  ${YELLOW}docker-compose down${NC}"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo -e "  README.md          - Project overview"
echo -e "  TESTING_GUIDE.md   - Complete testing & troubleshooting"
echo -e "  PROJECT_COMPLETE.md - Full feature summary"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo -e "  1. Send /start to your Telegram bot"
echo -e "  2. Click 'ORDER NOW' in the greeting"
echo -e "  3. Select menu items"
echo -e "  4. Watch live tracking widget update in real-time"
echo -e "  5. Admin panel: http://localhost:3000"
echo ""
echo -e "${YELLOW}⭐ Your café ordering platform is ready for production!${NC}"
