"""
BigQuery Sync API endpoints.

Provides REST endpoints to trigger data synchronization from BigQuery.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from scripts.sync_bigquery_data import sync_bigquery_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncRequest(BaseModel):
    """Request body for sync endpoints."""

    full_sync: bool = False
    sync_opportunities: bool = True
    sync_calls: bool = True


class SyncResponse(BaseModel):
    """Response from sync operations."""

    status: str
    start_time: str
    end_time: str
    duration_seconds: float
    full_sync: bool
    opportunities: dict[str, int] | None = None
    calls: dict[str, int] | None = None


@router.post("/bigquery", response_model=SyncResponse)
async def trigger_bigquery_sync(request: SyncRequest) -> dict[str, Any]:
    """
    Trigger BigQuery data sync.

    Syncs opportunities and/or calls from BigQuery to Postgres.
    Can be called by Vercel Cron or manually.
    """
    logger.info(
        f"BigQuery sync triggered: full_sync={request.full_sync}, "
        f"opportunities={request.sync_opportunities}, calls={request.sync_calls}"
    )

    try:
        result = sync_bigquery_data(
            sync_opportunities_flag=request.sync_opportunities,
            sync_calls_flag=request.sync_calls,
            full_sync=request.full_sync,
        )

        return {
            "status": "success",
            **result,
        }

    except Exception as e:
        logger.error(f"BigQuery sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/status")
async def get_sync_status() -> dict[str, Any]:
    """Get the last sync status for all entity types."""
    from db import queries

    try:
        opportunities_status = queries.get_sync_status("opportunities")
        calls_status = queries.get_sync_status("calls")

        return {
            "opportunities": opportunities_status,
            "calls": calls_status,
        }
    except Exception as e:
        logger.error(f"Failed to get sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
