"""
LearnMate FastAPI Application Entry Point
==========================================
All 10 design patterns are wired through the routers below.
Run: uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan: initialise singletons on startup ──

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise all Singleton services on startup."""
    logger.info("🚀 LearnMate backend starting up...")
    from app.patterns.creational.singletons import (
        AuthServiceSingleton,
        NotificationServiceSingleton,
        AIRecommendationEngineSingleton,
    )
    auth_svc   = AuthServiceSingleton()
    notif_svc  = NotificationServiceSingleton()
    ai_engine  = AIRecommendationEngineSingleton()

    ai_available = ai_engine.is_available()
    logger.info(f"✅ AuthServiceSingleton ready")
    logger.info(f"✅ NotificationServiceSingleton ready")
    logger.info(f"{'✅' if ai_available else '⚠️ '} AIRecommendationEngineSingleton ready (AI available: {ai_available})")
    logger.info("✅ All design pattern classes loaded")
    logger.info("🎯 Patterns active: Factory Method, Builder, Singleton, Facade, Adapter, Decorator, Observer, Strategy, State, Command")

    yield

    logger.info("👋 LearnMate backend shutting down...")


# ── App instance ──

app = FastAPI(
    title="LearnMate API",
    description="AI-Powered Personalized Learning Assistant — Backend API.\n\n**Design Patterns Implemented:** Factory Method, Builder, Singleton, Facade, Adapter, Decorator, Observer, Strategy, State, Command",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ── CORS ──

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.trycloudflare\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ──

from app.routers import (
    auth,
    courses,
    topics,
    quizzes,
    study_plans,
    recommendations,
    chat,
    notifications,
    groups,
    predictions,
    dashboard,
    profiles,
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(courses.router)
app.include_router(topics.router)
app.include_router(quizzes.router)
app.include_router(study_plans.router)
app.include_router(recommendations.router)
app.include_router(chat.router)
app.include_router(notifications.router)
app.include_router(groups.router)
app.include_router(predictions.router)
app.include_router(profiles.router)


# ── Health check ──

@app.get("/health", tags=["health"])
async def health():
    from app.services.database import get_supabase
    from app.patterns.creational.singletons import AIRecommendationEngineSingleton
    sb = get_supabase()
    ai = AIRecommendationEngineSingleton()
    return {
        "status": "ok",
        "supabase_connected": sb is not None,
        "ai_available": ai.is_available(),
        "patterns_loaded": [
            "Factory Method", "Builder", "Singleton",
            "Facade", "Adapter", "Decorator",
            "Observer", "Strategy", "State", "Command"
        ],
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "name": "LearnMate API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
