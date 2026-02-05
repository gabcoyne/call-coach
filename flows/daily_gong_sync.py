"""
Daily Gong synchronization flow.

Polls Gong API for opportunities, calls, and emails and caches in Neon PostgreSQL.
Supports both local execution (via uv run) and Vercel serverless function deployment.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any

from gong.client import GongClient
from db import queries

logger = logging.getLogger(__name__)


def sync_opportunities() -> dict[str, int]:
    """
    Sync opportunities from Gong API to database.

    Fetches opportunities modified since last sync and upserts to database.

    Returns:
        Dict with sync stats: {synced: int, errors: int}
    """
    logger.info("Starting opportunity sync")

    # Get last sync timestamp
    sync_status = queries.get_sync_status("opportunities")
    last_sync = sync_status["last_sync_timestamp"] if sync_status else None

    # Convert to ISO 8601 string for Gong API
    modified_after = last_sync.isoformat() if last_sync else None
    logger.info(f"Fetching opportunities modified after: {modified_after}")

    synced_count = 0
    error_count = 0
    errors = []

    try:
        with GongClient() as client:
            cursor = None
            while True:
                # Fetch page of opportunities
                opportunities, cursor = client.list_opportunities(
                    modified_after=modified_after,
                    cursor=cursor,
                )

                logger.info(f"Processing {len(opportunities)} opportunities")

                # Upsert each opportunity
                for opp in opportunities:
                    try:
                        # Extract fields from Gong API response
                        opp_data = {
                            "gong_opportunity_id": opp.get("id"),
                            "name": opp.get("name"),
                            "account_name": opp.get("account", {}).get("name"),
                            "owner_email": opp.get("owner", {}).get("emailAddress"),
                            "stage": opp.get("stage"),
                            "close_date": opp.get("closeDate"),
                            "amount": opp.get("amount"),
                            "health_score": opp.get("healthScore"),
                            "metadata": json.dumps(opp),  # Store full response as JSONB
                        }

                        queries.upsert_opportunity(opp_data)
                        synced_count += 1

                    except Exception as e:
                        error_count += 1
                        error_msg = f"Failed to sync opportunity {opp.get('id')}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)

                # Check if there are more pages
                if not cursor:
                    break

        # Update sync status
        queries.update_sync_status(
            entity_type="opportunities",
            status="success" if error_count == 0 else "partial",
            items_synced=synced_count,
            errors_count=error_count,
            error_details={"errors": errors} if errors else None,
        )

        logger.info(f"Opportunity sync complete: {synced_count} synced, {error_count} errors")
        return {"synced": synced_count, "errors": error_count}

    except Exception as e:
        logger.error(f"Opportunity sync failed: {e}")
        queries.update_sync_status(
            entity_type="opportunities",
            status="failed",
            items_synced=synced_count,
            errors_count=error_count + 1,
            error_details={"errors": errors + [str(e)]},
        )
        raise


def sync_opportunity_calls(opportunity_id: str, gong_opp_id: str) -> int:
    """
    Sync calls for a specific opportunity.

    Args:
        opportunity_id: Database opportunity UUID
        gong_opp_id: Gong opportunity ID

    Returns:
        Number of calls linked
    """
    linked_count = 0

    try:
        with GongClient() as client:
            cursor = None
            while True:
                # Fetch call IDs for opportunity
                call_ids, cursor = client.get_opportunity_calls(
                    opportunity_id=gong_opp_id,
                    cursor=cursor,
                )

                # Link each call to opportunity
                for gong_call_id in call_ids:
                    # Check if call exists in database
                    call_row = queries.get_call_by_gong_id(gong_call_id)
                    if call_row:
                        # Create junction record
                        queries.link_call_to_opportunity(
                            call_id=call_row["id"],
                            opp_id=opportunity_id,
                        )
                        linked_count += 1
                    else:
                        logger.warning(
                            f"Call {gong_call_id} not found in database, "
                            f"skipping link to opportunity {gong_opp_id}"
                        )

                if not cursor:
                    break

    except Exception as e:
        logger.error(f"Failed to sync calls for opportunity {gong_opp_id}: {e}")

    return linked_count


def sync_opportunity_emails(opportunity_id: str, gong_opp_id: str) -> int:
    """
    Sync emails for a specific opportunity.

    Args:
        opportunity_id: Database opportunity UUID
        gong_opp_id: Gong opportunity ID

    Returns:
        Number of emails synced
    """
    synced_count = 0

    try:
        with GongClient() as client:
            cursor = None
            while True:
                # Fetch emails for opportunity
                emails, cursor = client.get_opportunity_emails(
                    opportunity_id=gong_opp_id,
                    cursor=cursor,
                )

                # Upsert each email
                for email in emails:
                    try:
                        # Extract email body snippet (first 500 chars)
                        body = email.get("body", "")
                        body_snippet = body[:500] if body else None

                        email_data = {
                            "gong_email_id": email.get("id"),
                            "opportunity_id": opportunity_id,
                            "subject": email.get("subject"),
                            "sender_email": email.get("sender", {}).get("emailAddress"),
                            "recipients": [
                                r.get("emailAddress")
                                for r in email.get("recipients", [])
                                if r.get("emailAddress")
                            ],
                            "sent_at": email.get("sentAt"),
                            "body_snippet": body_snippet,
                            "metadata": json.dumps(email),
                        }

                        queries.upsert_email(email_data)
                        synced_count += 1

                    except Exception as e:
                        logger.error(f"Failed to sync email {email.get('id')}: {e}")

                if not cursor:
                    break

    except Exception as e:
        logger.error(f"Failed to sync emails for opportunity {gong_opp_id}: {e}")

    return synced_count


def sync_all_opportunity_associations() -> dict[str, int]:
    """
    Sync calls and emails for all opportunities in database.

    Returns:
        Dict with sync stats: {calls_linked: int, emails_synced: int}
    """
    logger.info("Starting sync of opportunity associations (calls and emails)")

    # Get all opportunities from database
    all_opps, _ = queries.search_opportunities(limit=10000)  # Get all

    total_calls = 0
    total_emails = 0

    for opp in all_opps:
        logger.info(f"Syncing associations for opportunity: {opp['name']}")

        # Sync calls
        calls_linked = sync_opportunity_calls(
            opportunity_id=opp["id"],
            gong_opp_id=opp["gong_opportunity_id"],
        )
        total_calls += calls_linked

        # Sync emails
        emails_synced = sync_opportunity_emails(
            opportunity_id=opp["id"],
            gong_opp_id=opp["gong_opportunity_id"],
        )
        total_emails += emails_synced

    logger.info(
        f"Association sync complete: {total_calls} calls linked, {total_emails} emails synced"
    )

    return {"calls_linked": total_calls, "emails_synced": total_emails}


def main() -> dict[str, Any]:
    """
    Main entry point for daily Gong sync.

    Executes full sync of opportunities, calls, and emails.

    Returns:
        Dict with sync results
    """
    start_time = datetime.now(timezone.utc)
    logger.info(f"Daily Gong sync started at {start_time.isoformat()}")

    try:
        # Step 1: Sync opportunities
        opp_results = sync_opportunities()

        # Step 2: Sync calls and emails for opportunities
        assoc_results = sync_all_opportunity_associations()

        # Calculate total time
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()

        results = {
            "status": "success",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "opportunities": opp_results,
            "associations": assoc_results,
        }

        logger.info(f"Daily Gong sync completed successfully in {duration:.1f}s")
        logger.info(f"Results: {json.dumps(results, indent=2)}")

        return results

    except Exception as e:
        logger.error(f"Daily Gong sync failed: {e}", exc_info=True)
        return {
            "status": "failed",
            "error": str(e),
            "start_time": start_time.isoformat(),
        }


if __name__ == "__main__":
    # Local execution: uv run python -m flows.daily_gong_sync
    from dotenv import load_dotenv

    load_dotenv()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run sync
    result = main()

    # Print results
    print("\n" + "=" * 80)
    print("DAILY GONG SYNC RESULTS")
    print("=" * 80)
    print(json.dumps(result, indent=2))
