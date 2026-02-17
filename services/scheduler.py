"""
Background scheduler service stub.

This is a minimal implementation that provides the expected interface
but doesn't actually schedule any tasks. In production, the data sync
is handled by the separate DLT Cloud Run Job with Cloud Scheduler.
"""

import logging

logger = logging.getLogger(__name__)

_scheduler_started = False


def get_scheduler():
    """Get the scheduler instance (stub)."""
    return None


def start_scheduler():
    """Start the background scheduler (stub).

    In production, data sync is handled by Cloud Run Jobs + Cloud Scheduler,
    so this is a no-op.
    """
    global _scheduler_started
    if _scheduler_started:
        logger.debug("Scheduler already started")
        return

    _scheduler_started = True
    logger.info("Scheduler stub initialized (data sync handled by Cloud Run Jobs)")


def stop_scheduler():
    """Stop the background scheduler (stub)."""
    global _scheduler_started
    _scheduler_started = False
    logger.info("Scheduler stub stopped")
