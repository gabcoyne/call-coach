"""
Content processor for converting scraped HTML to structured markdown.
Handles text cleanup, code extraction, and section hierarchy.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Processes scraped content into markdown format."""

    def __init__(self):
        self.min_content_length = 100
        self.max_content_length = 50000

    def process_document(self, doc: dict[str, Any]) -> dict[str, Any] | None:
        """
        Process a scraped document into clean markdown.

        Args:
            doc: Raw document from scraper

        Returns:
            Processed document with markdown content, or None if invalid
        """
        if not self._validate_document(doc):
            return None

        # Clean and normalize content
        content = self._clean_text(doc.get("content", ""))

        if not content or len(content) < self.min_content_length:
            logger.warning(f"Document {doc.get('url')} has insufficient content")
            return None

        # Trim if too long
        if len(content) > self.max_content_length:
            content = content[: self.max_content_length]

        # Convert to markdown
        markdown = self._convert_to_markdown(
            title=doc.get("title", ""),
            content=content,
            code_examples=doc.get("code_examples", []),
            url=doc.get("url", ""),
        )

        return {
            "title": doc.get("title", ""),
            "url": doc.get("url", ""),
            "product": doc.get("product", self._infer_product(doc.get("source", ""))),
            "category": doc.get("category", "general"),
            "source": doc.get("source", ""),
            "markdown_content": markdown,
            "code_examples": doc.get("code_examples", []),
            "config_examples": doc.get("config_examples", []),
            "sections": self._extract_sections(markdown),
        }

    def process_batch(self, documents: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Process multiple documents.

        Args:
            documents: List of raw documents

        Returns:
            List of processed documents
        """
        processed = []
        for doc in documents:
            result = self.process_document(doc)
            if result:
                processed.append(result)
        logger.info(f"Processed {len(processed)} of {len(documents)} documents")
        return processed

    def _validate_document(self, doc: dict[str, Any]) -> bool:
        """Validate that document has required fields."""
        required_fields = ["title", "url", "content"]
        for field in required_fields:
            if field not in doc or not doc[field]:
                logger.warning(f"Document missing required field: {field}")
                return False
        return True

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove common footer/navigation text
        footer_patterns = [
            r"Edit this page.*?GitHub",
            r"Was this helpful\?.*?",
            r"Copyright.*?\n",
            r"Terms.*?Privacy",
        ]
        for pattern in footer_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)

        # Remove redundant whitespace again
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def _convert_to_markdown(
        self,
        title: str,
        content: str,
        code_examples: list[str],
        url: str,
    ) -> str:
        """Convert content to markdown format."""
        md = f"# {title}\n\n"
        md += f"**Source:** {url}\n\n"

        # Add content
        md += content + "\n\n"

        # Add code examples if present
        if code_examples:
            md += "## Code Examples\n\n"
            for i, example in enumerate(code_examples, 1):
                # Try to detect language
                lang = self._detect_code_language(example)
                md += f"### Example {i}\n\n"
                md += f"```{lang}\n{example}\n```\n\n"

        return md.strip()

    def _detect_code_language(self, code: str) -> str:
        """Detect code language from content."""
        if "import " in code or "from " in code:
            return "python"
        elif "const " in code or "function" in code or "async" in code:
            return "javascript"
        elif "SELECT" in code.upper() or "INSERT" in code.upper():
            return "sql"
        elif "apiVersion:" in code or "kind:" in code:
            return "yaml"
        elif "{" in code and ":" in code:
            return "json"
        elif code.strip().startswith("<"):
            return "html"
        else:
            return "bash"

    def _extract_sections(self, markdown: str) -> list[str]:
        """Extract section headings from markdown."""
        sections = []
        for line in markdown.split("\n"):
            if line.startswith("##"):
                section = line.lstrip("#").strip()
                if section:
                    sections.append(section)
        return sections

    def _infer_product(self, source: str) -> str:
        """Infer product from source."""
        if "horizon" in source.lower():
            return "horizon"
        elif "prefect" in source.lower():
            return "prefect"
        else:
            return "unknown"


class CompetitiveAnalysisLoader:
    """Loads pre-written competitive analysis documents."""

    def __init__(self, docs_dir: str = "knowledge/competitive"):
        self.docs_dir = docs_dir

    def load_analysis(self, file_path: str) -> dict[str, Any] | None:
        """
        Load competitive analysis from file.

        Args:
            file_path: Path to markdown file

        Returns:
            Document structure with metadata
        """
        try:
            with open(file_path) as f:
                content = f.read()

            # Parse frontmatter if present
            metadata = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    import yaml

                    metadata = yaml.safe_load(parts[1])
                    content = parts[2]

            return {
                "title": metadata.get("title", "Competitive Analysis"),
                "category": "competitor",
                "product": metadata.get("product", "prefect"),
                "source": "competitive_analysis",
                "markdown_content": content.strip(),
                "metadata": metadata,
                "sections": self._extract_sections(content),
            }

        except Exception as e:
            logger.error(f"Error loading competitive analysis from {file_path}: {e}")
            return None

    def _extract_sections(self, markdown: str) -> list[str]:
        """Extract section headings from markdown."""
        sections = []
        for line in markdown.split("\n"):
            if line.startswith("##"):
                section = line.lstrip("#").strip()
                if section:
                    sections.append(section)
        return sections
