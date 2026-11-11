from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import asyncio

from app.config import settings
from app.database import engine, Base, async_session_maker
from app.schemas import HealthResponse

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")


async def init_demo_data():
    try:
        from init_demo_data import init_demo_data as init_data_func
        await init_data_func()
        logger.info("Demo data initialized successfully")
    except Exception as e:
        logger.warning(f"Demo data initialization skipped: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Café OS Backend", environment=settings.environment)
    await init_db()
    await init_demo_data()
    yield
    # Shutdown
    logger.info("Shutting down Café OS Backend")


app = FastAPI(
    title=settings.app_name,
    description="Premium Telegram Ordering Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment=settings.environment
    )


# Root
@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs"
    }


# API Routes will be mounted here
# Customer API routes
from app.api.customer import router as customer_router
app.include_router(customer_router, prefix="/api/v1", tags=["customer"])

# Admin API routes
from app.api.admin import router as admin_router
app.include_router(admin_router, prefix="/api/v1", tags=["admin"])

# Barista API routes
from app.api.barista import router as barista_router
app.include_router(barista_router, prefix="/api/v1", tags=["barista"])

# Telegram Bot webhook
from app.api.telegram_webhook import router as telegram_router
app.include_router(telegram_router, prefix="/api/v1", tags=["telegram"])

# Payment webhook
from app.api.payment_webhook import router as payment_router
app.include_router(payment_router, prefix="/api/v1", tags=["payment"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
