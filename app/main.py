from fastapi import FastAPI
from app.utils.logger import logger
from app.db.session import get_session
from app.api.v1 import (
    accounts_router,
    users_router,
    auth_router,
    transactions_router,
    insights_router,
    assistant_router,
    webhooks_router,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
from app.models import User
from app.core import settings
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("🚀 Application startup")
    yield
    logger.info("🛑 Application shutdown")


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    debug=settings.DEBUG,
    title="Trackify API",
    description="Trackify API for managing user accounts, transactions, and insights.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(accounts_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(insights_router)
app.include_router(assistant_router)
app.include_router(webhooks_router)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return {"status": "ok"}


@app.get("/api/v1/db-health")
async def db_health_check():
    """Database health check endpoint."""
    try:
        db = next(get_session())
        db.exec(select(User))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
