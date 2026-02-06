"""
Background task scheduler for automated Gong call imports.

This service runs scheduled tasks like:
- Importing new calls from Gong every hour
- Cleaning up old data
- Running batch analysis jobs
"""

import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from gong.client import GongClient
from scripts.import_calls import import_call_with_transcript

logger = logging.getLogger(__name__)


class CallCoachScheduler:
    """Background task scheduler for Call Coach."""

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            job_defaults={
                "coalesce": True,  # Combine missed runs
                "max_instances": 1,  # Only one instance of each job at a time
                "misfire_grace_time": 300,  # 5 minute grace period for missed jobs
            }
        )
        self.client = None

    def start(self):
        """Start the scheduler and register all jobs."""
        logger.info("Starting Call Coach scheduler...")

        # Initialize Gong client
        self.client = GongClient()

        # Schedule jobs
        self._schedule_hourly_import()
        self._schedule_daily_cleanup()

        # Start the scheduler
        self.scheduler.start()
        logger.info("Scheduler started successfully")

    def stop(self):
        """Gracefully stop the scheduler."""
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")

    def _schedule_hourly_import(self):
        """Import new calls from Gong every hour."""
        self.scheduler.add_job(
            func=self.import_recent_calls,
            trigger=IntervalTrigger(hours=1),
            id="hourly_gong_import",
            name="Import recent calls from Gong",
            replace_existing=True,
        )
        logger.info("Scheduled hourly Gong import")

    def _schedule_daily_cleanup(self):
        """Run daily cleanup tasks at 2 AM."""
        self.scheduler.add_job(
            func=self.cleanup_old_data,
            trigger=CronTrigger(hour=2, minute=0),
            id="daily_cleanup",
            name="Clean up old data",
            replace_existing=True,
        )
        logger.info("Scheduled daily cleanup at 2 AM")

    def import_recent_calls(self):
        """
        Import calls from the last 2 hours (with overlap to catch any missed).

        This job runs every hour and imports calls from the last 2 hours
        to ensure no calls are missed due to timing or processing delays.
        """
        try:
            logger.info("Starting scheduled Gong import...")

            # Calculate time range (last 2 hours with 15-minute buffer)
            to_date = datetime.utcnow() + timedelta(minutes=15)
            from_date = to_date - timedelta(hours=2)

            # Format as ISO 8601 with Z suffix for Gong API
            from_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
            to_date_str = to_date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"

            logger.info(f"Fetching calls from {from_date_str} to {to_date_str}")

            # Fetch calls from Gong
            calls, cursor = self.client.list_calls(
                from_date=from_date_str,
                to_date=to_date_str,
            )

            logger.info(f"Found {len(calls)} calls in time range")

            # Import each call
            imported_count = 0
            skipped_count = 0
            error_count = 0

            for call in calls:
                # Check if already imported (by gong_call_id)
                from db import queries

                existing_call = queries.get_call_by_gong_id(call.id)
                if existing_call:
                    logger.debug(f"Call {call.id} already exists, skipping")
                    skipped_count += 1
                    continue

                # Import the call
                if import_call_with_transcript(self.client, call):
                    imported_count += 1
                    logger.info(f"Successfully imported call {call.id}")
                else:
                    error_count += 1
                    logger.warning(f"Failed to import call {call.id}")

            logger.info(
                f"Import complete: {imported_count} imported, "
                f"{skipped_count} skipped, {error_count} errors"
            )

            return {
                "status": "success",
                "imported": imported_count,
                "skipped": skipped_count,
                "errors": error_count,
                "total_found": len(calls),
            }

        except Exception as e:
            logger.error(f"Scheduled import failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    def cleanup_old_data(self):
        """
        Clean up old data and perform maintenance tasks.

        This could include:
        - Archiving old calls
        - Cleaning up orphaned records
        - Vacuuming database tables
        """
        try:
            logger.info("Starting daily cleanup...")

            # Add cleanup logic here as needed
            # For now, just log that cleanup ran

            logger.info("Daily cleanup complete")

            return {"status": "success"}

        except Exception as e:
            logger.error(f"Cleanup failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}


# Global scheduler instance
_scheduler = None


def get_scheduler() -> CallCoachScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = CallCoachScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler."""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_scheduler():
    """Stop the global scheduler."""
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
