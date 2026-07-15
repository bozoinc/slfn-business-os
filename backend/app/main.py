"""
SLFN Nexus Platform - Backend API
An open-source alternative to HighLevel
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, contacts, deals, forms
from app.core.config import settings

app = FastAPI(
    title="SLFN Nexus Platform API",
    description="Open-source business operating system - HighLevel alternative",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    pass