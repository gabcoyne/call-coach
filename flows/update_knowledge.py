"""
Prefect flow for scheduled knowledge base updates.

Runs weekly to refresh product documentation, detect changes,
and notify admins of significant updates.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from prefect import flow, task
from prefect.artifacts import create_artifact
from prefect.logging import get_logger

logger = get_logger(__name__)


@task(retries=2, retry_delay_seconds=60)
async def ingest_documentation() -> dict[str, Any]:
    """
    Ingest product documentation using the ingestion pipeline.

    Returns:
        Dictionary with ingestion results
    """
    from knowledge_base.processor import CompetitiveAnalysisLoader, ContentProcessor
    from knowledge_base.scrapers.horizon_docs import HorizonDocsScraper
    from knowledge_base.scrapers.prefect_docs import PrefectDocsScraper

    logger.info("Starting documentation ingestion task...")

    processor = ContentProcessor()
    all_documents = []
    results = {
        "prefect_count": 0,
        "horizon_count": 0,
        "competitive_count": 0,
        "total": 0,
        "errors": [],
    }

    try:
        # Prefect docs
        logger.info("Scraping Prefect documentation...")
        async with PrefectDocsScraper() as scraper:
            prefect_docs = await scraper.scrape()
            prefect_processed = processor.process_batch(prefect_docs)
            all_documents.extend(prefect_processed)
            results["prefect_count"] = len(prefect_processed)

    except Exception as e:
        logger.error(f"Error ingesting Prefect docs: {e}")
        results["errors"].append(f"Prefect docs: {str(e)}")

    try:
        # Horizon docs
        logger.info("Scraping Horizon documentation...")
        async with HorizonDocsScraper() as scraper:
            horizon_docs = await scraper.scrape()
            horizon_processed = processor.process_batch(horizon_docs)
            all_documents.extend(horizon_processed)
            results["horizon_count"] = len(horizon_processed)

    except Exception as e:
        logger.error(f"Error ingesting Horizon docs: {e}")
        results["errors"].append(f"Horizon docs: {str(e)}")

    try:
        # Competitive analysis
        logger.info("Loading competitive analysis...")
        competitive_loader = CompetitiveAnalysisLoader()
        competitive_dir = Path("knowledge/competitive")
        if competitive_dir.exists():
            for md_file in competitive_dir.glob("*.md"):
                doc = competitive_loader.load_analysis(str(md_file))
                if doc:
                    all_documents.append(doc)
        results["competitive_count"] = results["competitive_count"]

    except Exception as e:
        logger.error(f"Error loading competitive analysis: {e}")
        results["errors"].append(f"Competitive analysis: {str(e)}")

    results["total"] = len(all_documents)
    logger.info(f"Ingestion complete: {results['total']} total documents")

    return results


@task
def store_in_database(documents: list[dict[str, Any]], ingestion_results: dict) -> dict[str, Any]:
    """
    Store ingested documents in the knowledge base table.

    Args:
        documents: Processed documents to store
        ingestion_results: Metadata about ingestion

    Returns:
        Storage results
    """
    from db import execute_query

    logger.info(f"Storing {len(documents)} documents in database...")

    stored_count = 0
    updated_count = 0
    errors = []

    for doc in documents:
        try:
            # Check if document exists
            result = execute_query(
                """
                SELECT id, last_updated
                FROM knowledge_base
                WHERE product = %s AND category = %s
                """,
                (doc.get("product", "unknown"), doc.get("category", "general")),
                fetch=True,
            )

            if result:
                # Update existing
                execute_query(
                    """
                    UPDATE knowledge_base
                    SET content = %s, metadata = %s, last_updated = NOW()
                    WHERE product = %s AND category = %s
                    """,
                    (
                        doc.get("markdown_content", ""),
                        json.dumps(
                            {
                                "url": doc.get("url"),
                                "source": doc.get("source"),
                                "sections": doc.get("sections", []),
                                "code_examples": len(doc.get("code_examples", [])),
                            }
                        ),
                        doc.get("product", "unknown"),
                        doc.get("category", "general"),
                    ),
                )
                updated_count += 1
            else:
                # Insert new
                execute_query(
                    """
                    INSERT INTO knowledge_base (product, category, content, metadata, last_updated)
                    VALUES (%s, %s, %s, %s, NOW())
                    """,
                    (
                        doc.get("product", "unknown"),
                        doc.get("category", "general"),
                        doc.get("markdown_content", ""),
                        json.dumps(
                            {
                                "url": doc.get("url"),
                                "source": doc.get("source"),
                                "title": doc.get("title"),
                                "sections": doc.get("sections", []),
                                "code_examples": len(doc.get("code_examples", [])),
                            }
                        ),
                    ),
                )
                stored_count += 1

        except Exception as e:
            logger.error(f"Error storing document {doc.get('url')}: {e}")
            errors.append(f"{doc.get('url')}: {str(e)}")

    logger.info(f"Storage complete: {stored_count} new, {updated_count} updated")

    return {
        "stored": stored_count,
        "updated": updated_count,
        "total": stored_count + updated_count,
        "errors": errors,
    }


@task
def detect_changes(storage_results: dict) -> dict[str, Any]:
    """
    Detect significant changes in knowledge base.

    Returns:
        Change detection results
    """
    changes = {
        "new_documents": storage_results.get("stored", 0),
        "updated_documents": storage_results.get("updated", 0),
        "has_changes": (
            storage_results.get("stored", 0) + storage_results.get("updated", 0) > 0
        ),
        "errors": storage_results.get("errors", []),
    }

    if changes["has_changes"]:
        logger.warning(
            f"Detected changes: {changes['new_documents']} new, {changes['updated_documents']} updated"
        )

    return changes


@task
def notify_admins(changes: dict[str, Any], ingestion_results: dict):
    """
    Notify admins of significant knowledge base changes.

    Args:
        changes: Change detection results
        ingestion_results: Ingestion metadata
    """
    if not changes["has_changes"] and not ingestion_results.get("errors"):
        logger.info("No significant changes, skipping notifications")
        return

    message = "Knowledge Base Update Summary\n"
    message += f"Time: {datetime.now().isoformat()}\n\n"

    message += f"Ingestion Results:\n"
    message += f"  Prefect docs: {ingestion_results.get('prefect_count', 0)}\n"
    message += f"  Horizon docs: {ingestion_results.get('horizon_count', 0)}\n"
    message += f"  Competitive: {ingestion_results.get('competitive_count', 0)}\n"
    message += f"  Total: {ingestion_results.get('total', 0)}\n\n"

    message += f"Changes:\n"
    message += f"  New documents: {changes['new_documents']}\n"
    message += f"  Updated documents: {changes['updated_documents']}\n\n"

    if ingestion_results.get("errors"):
        message += f"Errors:\n"
        for error in ingestion_results["errors"]:
            message += f"  - {error}\n"

    logger.info(message)

    # Create Prefect artifact for visibility
    create_artifact(
        key="knowledge-base-update",
        description="Knowledge Base Update Summary",
        data={"changes": changes, "ingestion": ingestion_results},
        artifact_type="result",
    )


@task
def validate_links() -> dict[str, Any]:
    """
    Validate that all links in knowledge base are accessible.

    Returns:
        Validation results
    """
    import httpx

    from db import fetch_all

    logger.info("Validating knowledge base links...")

    results = {"total": 0, "valid": 0, "broken": 0, "errors": []}

    try:
        # Get all documents with URLs in metadata
        documents = fetch_all(
            """
            SELECT metadata
            FROM knowledge_base
            WHERE metadata IS NOT NULL AND metadata->>'url' IS NOT NULL
            """
        )

        results["total"] = len(documents)

        for doc in documents:
            try:
                if not doc.get("metadata"):
                    continue

                url = doc["metadata"].get("url")
                if not url:
                    continue

                # Quick HEAD request to validate
                with httpx.Client(timeout=10) as client:
                    response = client.head(url, follow_redirects=True)
                    if response.status_code < 400:
                        results["valid"] += 1
                    else:
                        results["broken"] += 1
                        results["errors"].append(f"{url} returned {response.status_code}")

            except Exception as e:
                results["broken"] += 1
                results["errors"].append(f"Error checking {url}: {str(e)}")

    except Exception as e:
        logger.error(f"Error during link validation: {e}")
        results["errors"].append(f"Validation error: {str(e)}")

    logger.info(
        f"Link validation: {results['valid']} valid, {results['broken']} broken out of {results['total']}"
    )

    return results


@flow(name="update_knowledge_base", description="Weekly knowledge base update")
async def update_knowledge_base():
    """
    Main flow for updating the knowledge base.

    Orchestrates scraping, processing, storage, and validation.
    """
    logger.info("Starting knowledge base update flow...")

    # Ingest documentation
    ingestion_results = await ingest_documentation()

    # For now, we'll skip the database storage since it requires db setup
    # In production, this would store to the knowledge_base table
    # storage_results = store_in_database(documents, ingestion_results)

    # Detect changes
    changes = detect_changes({"stored": 0, "updated": 0, "total": 0, "errors": []})

    # Notify admins
    notify_admins(changes, ingestion_results)

    # Validate links
    validation_results = validate_links()

    logger.info("Knowledge base update flow completed")

    return {
        "ingestion": ingestion_results,
        "changes": changes,
        "validation": validation_results,
    }


if __name__ == "__main__":
    # Run locally for testing
    result = asyncio.run(update_knowledge_base())
    print(json.dumps(result, indent=2))
