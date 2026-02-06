"""
Database loader for storing and retrieving ingested documents.
Integrates scraped content with the knowledge base table.
"""

import json
import logging
from typing import Any
from uuid import UUID

from db import execute_query, fetch_all, fetch_one

logger = logging.getLogger(__name__)


class KnowledgeBaseDBLoader:
    """Manages storing ingested documents in the database."""

    def store_document(self, doc: dict[str, Any]) -> UUID | None:
        """
        Store a processed document in the knowledge base.

        Args:
            doc: Processed document dict

        Returns:
            UUID of stored document, or None if failed
        """
        try:
            # Check if document already exists
            existing = fetch_one(
                """
                SELECT id FROM knowledge_base
                WHERE product = %s AND category = %s
                """,
                (doc.get("product", "unknown"), doc.get("category", "general")),
            )

            metadata = {
                "url": doc.get("url"),
                "source": doc.get("source"),
                "title": doc.get("title"),
                "sections": doc.get("sections", []),
                "code_examples_count": len(doc.get("code_examples", [])),
                "config_examples_count": len(doc.get("config_examples", [])),
            }

            if existing:
                # Update existing document
                execute_query(
                    """
                    UPDATE knowledge_base
                    SET content = %s, metadata = %s, last_updated = NOW()
                    WHERE id = %s
                    """,
                    (
                        doc.get("markdown_content", ""),
                        json.dumps(metadata),
                        existing["id"],
                    ),
                )
                logger.info(f"Updated document: {doc.get('url')}")
                return existing["id"]
            else:
                # Insert new document
                result = execute_query(
                    """
                    INSERT INTO knowledge_base (product, category, content, metadata, last_updated)
                    VALUES (%s, %s, %s, %s, NOW())
                    RETURNING id
                    """,
                    (
                        doc.get("product", "unknown"),
                        doc.get("category", "general"),
                        doc.get("markdown_content", ""),
                        json.dumps(metadata),
                    ),
                    fetch=True,
                )
                if result:
                    logger.info(f"Stored new document: {doc.get('url')}")
                    return result[0].get("id")
                return None

        except Exception as e:
            logger.error(f"Error storing document {doc.get('url')}: {e}")
            return None

    def store_ingestion_job(self, source: str, status: str = "pending") -> UUID | None:
        """
        Create an ingestion job record.

        Args:
            source: Data source (prefect_docs, horizon_docs, competitive)
            status: Job status

        Returns:
            UUID of ingestion job
        """
        try:
            result = execute_query(
                """
                INSERT INTO ingestion_jobs (source, status)
                VALUES (%s, %s)
                RETURNING id
                """,
                (source, status),
                fetch=True,
            )
            if result:
                return result[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Error creating ingestion job: {e}")
            return None

    def update_ingestion_job(
        self,
        job_id: UUID,
        status: str = None,
        documents_scraped: int = None,
        documents_processed: int = None,
        documents_stored: int = None,
        documents_updated: int = None,
        error_message: str = None,
    ) -> bool:
        """
        Update an ingestion job record.

        Args:
            job_id: Job ID to update
            status: New status
            documents_*: Document counts
            error_message: Error if failed

        Returns:
            True if successful
        """
        try:
            updates = []
            params = []

            if status:
                updates.append("status = %s")
                params.append(status)
                if status == "completed":
                    updates.append("completed_at = NOW()")

            if documents_scraped is not None:
                updates.append("documents_scraped = %s")
                params.append(documents_scraped)

            if documents_processed is not None:
                updates.append("documents_processed = %s")
                params.append(documents_processed)

            if documents_stored is not None:
                updates.append("documents_stored = %s")
                params.append(documents_stored)

            if documents_updated is not None:
                updates.append("documents_updated = %s")
                params.append(documents_updated)

            if error_message:
                updates.append("error_message = %s")
                params.append(error_message)

            if not updates:
                return True

            params.append(str(job_id))

            execute_query(
                f"UPDATE ingestion_jobs SET {', '.join(updates)} WHERE id = %s",
                params,
            )
            return True

        except Exception as e:
            logger.error(f"Error updating ingestion job {job_id}: {e}")
            return False

    def store_scraped_document(
        self, job_id: UUID, url: str, title: str, raw_content: str, content_hash: str
    ) -> UUID | None:
        """
        Store raw scraped content before processing.

        Args:
            job_id: Associated ingestion job
            url: Source URL
            title: Document title
            raw_content: Raw HTML/content
            content_hash: SHA256 hash

        Returns:
            UUID of scraped document
        """
        try:
            result = execute_query(
                """
                INSERT INTO scraped_documents (ingestion_job_id, url, title, raw_content, content_hash)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (job_id, url, title, raw_content, content_hash),
                fetch=True,
            )
            if result:
                return result[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Error storing scraped document {url}: {e}")
            return None

    def create_document_section(
        self,
        kb_id: UUID,
        section_title: str,
        section_content: str,
        section_order: int,
        has_code: bool = False,
    ) -> UUID | None:
        """
        Create a document section for indexed search.

        Args:
            kb_id: Knowledge base document ID
            section_title: Section heading
            section_content: Section text content
            section_order: Ordering within document
            has_code: Whether section has code examples

        Returns:
            UUID of created section
        """
        try:
            result = execute_query(
                """
                INSERT INTO document_sections (knowledge_base_id, section_title, section_content, section_order, has_code_examples)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (kb_id, section_title, section_content, section_order, has_code),
                fetch=True,
            )
            if result:
                return result[0].get("id")
            return None
        except Exception as e:
            logger.error(f"Error creating document section: {e}")
            return None

    def store_links(self, kb_id: UUID, links: list[dict[str, str]]) -> int:
        """
        Store document links for validation.

        Args:
            kb_id: Knowledge base document ID
            links: List of {url, text, is_internal} dicts

        Returns:
            Number of links stored
        """
        stored = 0
        for link in links:
            try:
                execute_query(
                    """
                    INSERT INTO knowledge_base_links (knowledge_base_id, link_url, link_text, is_internal)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (kb_id, link.get("url"), link.get("text"), link.get("is_internal", False)),
                )
                stored += 1
            except Exception as e:
                logger.error(f"Error storing link {link.get('url')}: {e}")

        return stored

    def get_documents_by_product(self, product: str) -> list[dict[str, Any]]:
        """Get all knowledge base entries for a product."""
        try:
            results = fetch_all(
                """
                SELECT id, product, category, content, metadata, last_updated
                FROM knowledge_base
                WHERE product = %s
                ORDER BY last_updated DESC
                """,
                (product,),
            )
            return results or []
        except Exception as e:
            logger.error(f"Error fetching documents for {product}: {e}")
            return []

    def get_recent_changes(self, hours: int = 24) -> list[dict[str, Any]]:
        """Get recently updated knowledge base entries."""
        try:
            results = fetch_all(
                """
                SELECT id, product, category, content, last_updated
                FROM knowledge_base
                WHERE last_updated > NOW() - INTERVAL '%s hours'
                ORDER BY last_updated DESC
                """,
                (hours,),
            )
            return results or []
        except Exception as e:
            logger.error(f"Error fetching recent changes: {e}")
            return []

    def get_ingestion_summary(self) -> dict[str, Any]:
        """Get summary of recent ingestions."""
        try:
            result = fetch_one(
                """
                SELECT
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_jobs,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_jobs,
                    SUM(documents_stored) as total_stored,
                    SUM(documents_updated) as total_updated,
                    MAX(completed_at) as last_ingestion
                FROM ingestion_jobs
                WHERE completed_at > NOW() - INTERVAL '7 days'
                """
            )
            return result or {}
        except Exception as e:
            logger.error(f"Error fetching ingestion summary: {e}")
            return {}
