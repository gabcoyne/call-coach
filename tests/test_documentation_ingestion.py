"""
Tests for documentation ingestion system.
"""
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from knowledge_base.processor import ContentProcessor, CompetitiveAnalysisLoader
from knowledge_base.validator import ComplianceValidator, DocumentationValidator


class TestContentProcessor:
    """Tests for content processing."""

    def test_clean_text(self):
        """Test text cleaning."""
        processor = ContentProcessor()

        text = "Hello   world  \n\n   this is   messy"
        cleaned = processor._clean_text(text)
        assert "Hello world" in cleaned
        assert "\n\n" not in cleaned

    def test_validate_document(self):
        """Test document validation."""
        processor = ContentProcessor()

        valid_doc = {
            "title": "Test Document",
            "url": "https://example.com",
            "content": "This is valid content with sufficient length to pass validation",
        }
        assert processor._validate_document(valid_doc)

        invalid_doc = {"title": "Test"}
        assert not processor._validate_document(invalid_doc)

    def test_process_document(self):
        """Test document processing."""
        processor = ContentProcessor()

        doc = {
            "title": "Introduction to Prefect",
            "url": "https://docs.prefect.io/intro",
            "content": "Prefect is a workflow orchestration framework. " * 10,
            "source": "prefect_docs",
            "category": "guide",
            "code_examples": ["import prefect"],
        }

        result = processor.process_document(doc)
        assert result is not None
        assert result["title"] == "Introduction to Prefect"
        assert "markdown_content" in result
        assert result["product"] == "prefect"

    def test_detect_code_language(self):
        """Test code language detection."""
        processor = ContentProcessor()

        assert processor._detect_code_language("import os\nfrom pathlib import Path") == "python"
        assert (
            processor._detect_code_language("const x = 5; async function test() {}")
            == "javascript"
        )
        assert processor._detect_code_language("SELECT * FROM users") == "sql"
        assert processor._detect_code_language("apiVersion: v1\nkind: Pod") == "yaml"

    def test_extract_sections(self):
        """Test section extraction."""
        processor = ContentProcessor()

        markdown = """
        # Title
        Content here
        ## Section 1
        More content
        ## Section 2
        """

        sections = processor._extract_sections(markdown)
        assert "Section 1" in sections
        assert "Section 2" in sections
        assert len(sections) == 2


class TestDocumentationValidator:
    """Tests for documentation validation."""

    def test_validate_structure(self):
        """Test document structure validation."""
        validator = DocumentationValidator()

        valid_doc = {
            "title": "Test Document",
            "url": "https://docs.example.com/test",
            "product": "prefect",
            "category": "guide",
            "markdown_content": "This is valid content " * 20,
            "metadata": {"source": "test"},
        }

        result = validator.validate_structure(valid_doc)
        assert result["valid"]
        assert len(result["issues"]) == 0

    def test_validate_structure_invalid_url(self):
        """Test validation with invalid URL."""
        validator = DocumentationValidator()

        invalid_doc = {
            "title": "Test",
            "url": "not-a-url",
            "product": "prefect",
            "category": "guide",
            "markdown_content": "Content " * 20,
        }

        result = validator.validate_structure(invalid_doc)
        assert not result["valid"]
        assert len(result["issues"]) > 0

    def test_validate_structure_short_content(self):
        """Test validation with insufficient content."""
        validator = DocumentationValidator()

        short_doc = {
            "title": "Test",
            "url": "https://example.com",
            "product": "prefect",
            "category": "guide",
            "markdown_content": "Too short",
        }

        result = validator.validate_structure(short_doc)
        assert not result["valid"]

    def test_extract_internal_links(self):
        """Test internal link extraction."""
        validator = DocumentationValidator()

        doc = {
            "markdown_content": "[Guide](/docs/guide) and [External](https://example.com) and [Anchor](#section)"
        }

        links = validator.extract_internal_links(doc)
        assert len(links) == 3
        assert any(l["text"] == "Guide" and l["is_internal"] for l in links)
        assert any(l["text"] == "External" and not l["is_internal"] for l in links)

    def test_compare_versions(self):
        """Test version comparison."""
        validator = DocumentationValidator()

        old_doc = {
            "title": "Document v1",
            "markdown_content": "Original content",
            "sections": ["Intro", "Setup"],
        }

        new_doc = {
            "title": "Document v2",
            "markdown_content": "Updated content",
            "sections": ["Intro", "Setup", "Advanced"],
        }

        changes = validator.compare_versions(old_doc, new_doc)
        assert changes["title_changed"]
        assert changes["content_changed"]
        assert changes["sections_added"] == 1


class TestComplianceValidator:
    """Tests for compliance validation."""

    def test_validate_seo_metadata(self):
        """Test SEO validation."""
        validator = ComplianceValidator()

        good_doc = {
            "title": "Introduction to Prefect Workflows",
            "markdown_content": "Prefect is a workflow orchestration " * 20,
            "url": "https://docs.prefect.io/intro",
        }

        result = validator.validate_seo_metadata(good_doc)
        assert result["valid"]
        assert result["title_length"] > 10

    def test_validate_accessibility(self):
        """Test accessibility validation."""
        validator = ComplianceValidator()

        good_doc = {
            "markdown_content": """
            ## Installation
            Install with pip

            ```bash
            pip install prefect
            ```

            ## Configuration
            Configure your workflow
            """,
            "code_examples": ["pip install prefect"],
            "sections": ["Installation", "Configuration"],
        }

        result = validator.validate_accessibility(good_doc)
        assert result["valid"]
        assert result["has_structure"]


class TestCompetitiveAnalysisLoader:
    """Tests for competitive analysis loading."""

    def test_load_analysis(self, tmp_path):
        """Test loading competitive analysis."""
        md_file = tmp_path / "test.md"
        md_file.write_text(
            """---
title: "Prefect vs Airflow"
product: "prefect"
---

# Comparison
Prefect is better
"""
        )

        loader = CompetitiveAnalysisLoader()
        result = loader.load_analysis(str(md_file))

        assert result is not None
        assert result["title"] == "Prefect vs Airflow"
        assert result["product"] == "prefect"
        assert "Comparison" in result["markdown_content"]

    def test_extract_sections(self):
        """Test section extraction from markdown."""
        loader = CompetitiveAnalysisLoader()

        markdown = """
        # Title
        ## Section 1
        Content
        ## Section 2
        More content
        """

        sections = loader._extract_sections(markdown)
        assert "Section 1" in sections
        assert "Section 2" in sections


class TestBatchProcessing:
    """Tests for batch processing."""

    def test_process_batch(self):
        """Test processing multiple documents."""
        processor = ContentProcessor()

        docs = [
            {
                "title": f"Document {i}",
                "url": f"https://example.com/doc{i}",
                "content": f"Content for document {i} " * 20,
                "source": "test_source",
                "category": "guide",
            }
            for i in range(3)
        ]

        results = processor.process_batch(docs)
        assert len(results) == 3
        assert all("markdown_content" in r for r in results)


@pytest.mark.asyncio
async def test_validator_link_validation_mock():
    """Test link validation with mocking."""

    async def mock_head(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        return response

    validator = DocumentationValidator()
    validator.session = AsyncMock()
    validator.session.head = mock_head

    result = await validator.validate_link("https://example.com")
    assert result["status"] == "valid"
    assert result["http_status"] == 200


class TestContentDetection:
    """Tests for content type detection."""

    def test_infer_product(self):
        """Test product inference."""
        processor = ContentProcessor()

        assert processor._infer_product("prefect_docs") == "prefect"
        assert processor._infer_product("horizon_docs") == "horizon"
        assert processor._infer_product("other_source") == "unknown"

    def test_categorize_page(self):
        """Test page categorization based on URL."""
        from knowledge_base.scrapers.prefect_docs import PrefectDocsScraper

        scraper = PrefectDocsScraper()

        assert scraper._categorize_page("https://docs.prefect.io/guide/") == "guide"
        assert scraper._categorize_page("https://docs.prefect.io/concepts/") == "concepts"
        assert scraper._categorize_page("https://docs.prefect.io/api/") == "api"
        assert scraper._categorize_page("https://docs.prefect.io/tutorials/") == "tutorial"
