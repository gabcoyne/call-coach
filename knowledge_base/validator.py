"""
Validation utilities for ingested documentation.
Checks links, structure, and completeness.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


class DocumentationValidator:
    """Validates ingested documentation for quality and completeness."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    async def validate_link(self, url: str, follow_redirects: bool = True) -> dict[str, Any]:
        """
        Validate that a link is accessible.

        Args:
            url: URL to validate
            follow_redirects: Whether to follow HTTP redirects

        Returns:
            Validation result with status and details
        """
        if not self.session:
            return {"url": url, "status": "error", "message": "Session not initialized"}

        try:
            response = await self.session.head(
                url, follow_redirects=follow_redirects, allow_redirects=True
            )
            status = "valid" if response.status_code < 400 else "broken"
            return {
                "url": url,
                "status": status,
                "http_status": response.status_code,
                "message": f"HTTP {response.status_code}",
            }

        except httpx.ConnectError:
            return {
                "url": url,
                "status": "broken",
                "http_status": 0,
                "message": "Connection failed",
            }
        except httpx.TimeoutException:
            return {"url": url, "status": "timeout", "http_status": 0, "message": "Request timeout"}
        except Exception as e:
            return {"url": url, "status": "error", "http_status": 0, "message": str(e)}

    async def validate_links_batch(self, urls: list[str]) -> list[dict[str, Any]]:
        """
        Validate multiple links concurrently.

        Args:
            urls: List of URLs to validate

        Returns:
            List of validation results
        """
        tasks = [self.validate_link(url) for url in urls]
        return await asyncio.gather(*tasks)

    def validate_structure(self, document: dict[str, Any]) -> dict[str, Any]:
        """
        Validate document structure and required fields.

        Args:
            document: Document to validate

        Returns:
            Validation result with any issues found
        """
        issues = []
        warnings = []

        # Check required fields
        required_fields = ["title", "url", "product", "category", "markdown_content"]
        for field in required_fields:
            if field not in document or not document[field]:
                issues.append(f"Missing required field: {field}")

        # Check content length
        content = document.get("markdown_content", "")
        if len(content) < 100:
            issues.append("Document content is too short (< 100 chars)")
        elif len(content) > 50000:
            warnings.append("Document content is very long (> 50KB)")

        # Check for sections
        if not document.get("sections"):
            warnings.append("No sections extracted from document")

        # Validate URL format
        try:
            parsed = urlparse(document.get("url", ""))
            if not parsed.scheme or not parsed.netloc:
                issues.append("Invalid URL format")
        except Exception:
            issues.append("Could not parse URL")

        # Check metadata
        if not document.get("metadata"):
            warnings.append("Missing metadata")

        # Validate category
        valid_categories = [
            "feature",
            "differentiation",
            "use_case",
            "pricing",
            "competitor",
            "guide",
            "concepts",
            "api",
            "tutorial",
            "faq",
            "general",
            "account_management",
            "configuration",
            "deployment",
            "authentication",
            "integrations",
            "overview",
        ]
        if document.get("category") not in valid_categories:
            warnings.append(f"Unknown category: {document.get('category')}")

        # Validate product
        valid_products = ["prefect", "horizon", "unknown"]
        if document.get("product") not in valid_products:
            warnings.append(f"Unknown product: {document.get('product')}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "timestamp": datetime.now().isoformat(),
        }

    def extract_internal_links(self, document: dict[str, Any]) -> list[dict[str, str]]:
        """
        Extract all links from document markdown.

        Args:
            document: Document to extract links from

        Returns:
            List of {url, text, is_internal} dicts
        """
        links = []
        markdown = document.get("markdown_content", "")

        # Find markdown links [text](url)
        import re

        pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        matches = re.finditer(pattern, markdown)

        for match in matches:
            text = match.group(1)
            url = match.group(2)

            # Determine if internal link
            is_internal = not url.startswith(("http://", "https://")) and not url.startswith("#")

            links.append({"url": url, "text": text, "is_internal": is_internal})

        return links

    def compare_versions(self, old_doc: dict[str, Any], new_doc: dict[str, Any]) -> dict[str, Any]:
        """
        Compare two versions of a document to detect changes.

        Args:
            old_doc: Previous document version
            new_doc: New document version

        Returns:
            Change summary
        """
        changes = {
            "title_changed": old_doc.get("title") != new_doc.get("title"),
            "content_changed": old_doc.get("markdown_content") != new_doc.get("markdown_content"),
            "category_changed": old_doc.get("category") != new_doc.get("category"),
            "old_sections": len(old_doc.get("sections", [])),
            "new_sections": len(new_doc.get("sections", [])),
            "sections_added": len(
                set(new_doc.get("sections", [])) - set(old_doc.get("sections", []))
            ),
            "sections_removed": len(
                set(old_doc.get("sections", [])) - set(new_doc.get("sections", []))
            ),
        }

        # Calculate content similarity (simple word-based)
        old_words = set(old_doc.get("markdown_content", "").split())
        new_words = set(new_doc.get("markdown_content", "").split())
        if old_words or new_words:
            similarity = len(old_words & new_words) / len(old_words | new_words)
            changes["content_similarity"] = round(similarity, 2)

        return changes


class ComplianceValidator:
    """Validates documentation compliance with standards."""

    def validate_seo_metadata(self, document: dict[str, Any]) -> dict[str, Any]:
        """
        Validate SEO metadata in document.

        Returns:
            SEO validation results
        """
        issues = []

        title = document.get("title", "")
        if not title or len(title) < 10:
            issues.append("Title too short or missing")
        elif len(title) > 70:
            issues.append("Title too long (> 70 chars)")

        content = document.get("markdown_content", "")
        if len(content) < 300:
            issues.append("Content too short for good SEO (< 300 chars)")

        # Check for keywords
        url = document.get("url", "").lower()
        title_lower = title.lower()
        if not any(
            word in title_lower for word in ["prefect", "horizon", "workflow", "orchestration"]
        ):
            issues.append("Missing relevant keywords in title")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "title_length": len(title),
            "content_length": len(content),
        }

    def validate_accessibility(self, document: dict[str, Any]) -> dict[str, Any]:
        """
        Validate accessibility standards in document.

        Returns:
            Accessibility validation results
        """
        issues = []

        # Check for code examples without language specification
        code_examples = document.get("code_examples", [])
        if code_examples and not any("```" in ex for ex in code_examples):
            issues.append("Code examples may not be properly formatted")

        # Check content structure
        sections = document.get("sections", [])
        if not sections:
            issues.append("No clear section structure (missing headings)")

        # Check for descriptive links
        markdown = document.get("markdown_content", "")
        generic_links = ["click here", "read more", "link"]
        for link_text in generic_links:
            if link_text.lower() in markdown.lower():
                issues.append(f"Found generic link text: '{link_text}'")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "has_structure": len(sections) > 0,
            "code_examples_count": len(code_examples),
        }
