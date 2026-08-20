"""
SLFN Nexus Platform - Backend API
An open-source alternative to HighLevel
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, contacts, deals, forms, auth, guidance, documents
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run on application startup and shutdown"""
    # Startup
    yield
    # Shutdown

app = FastAPI(
    title="SLFN Nexus Platform API",
    description="Open-source business operating system - HighLevel alternative",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(contacts.router, prefix="/api/v1", tags=["contacts"])
app.include_router(deals.router, prefix="/api/v1", tags=["deals"])
app.include_router(forms.router, prefix="/api/v1", tags=["forms"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(guidance.router, prefix="/api/v1", tags=["guidance"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])