"""
API v1 routes.

Version 1 of the Call Coaching API with:
- Versioned endpoints under /api/v1/
- Stable response schemas
- Deprecation warnings for future changes
"""

from fastapi import APIRouter

from .calls import router as calls_router
from .opportunities import router as opportunities_router
from .rubrics import router as rubrics_router
from .speakers import router as speakers_router
from .team import router as team_router
from .tools import router as tools_router
from .users import router as users_router

# Main v1 router
router = APIRouter(prefix="/api/v1")

# Include sub-routers
router.include_router(tools_router, prefix="/tools", tags=["tools"])
router.include_router(users_router)
router.include_router(team_router)
router.include_router(calls_router)
router.include_router(opportunities_router)
router.include_router(speakers_router)
router.include_router(rubrics_router)

__all__ = ["router"]
