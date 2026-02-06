"""
API v1 routes.

Version 1 of the Call Coaching API with:
- Versioned endpoints under /api/v1/
- Stable response schemas
- Deprecation warnings for future changes
"""
from fastapi import APIRouter

from .tools import router as tools_router

# Main v1 router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(tools_router, prefix="/tools", tags=["tools"])

__all__ = ["router"]
