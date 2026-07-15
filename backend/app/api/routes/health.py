"""API routes - Health check endpoint"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="Health Check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "slfn-nexus-platform",
        "version": "0.1.0",
    }