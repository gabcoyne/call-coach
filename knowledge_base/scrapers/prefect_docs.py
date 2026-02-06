"""
Scraper for Prefect documentation (docs.prefect.io).
Extracts features, use cases, API documentation, and tutorials.
"""

import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class PrefectDocsScraper(BaseScraper):
    """Scrapes Prefect product documentation."""

    def __init__(self):
        super().__init__(
            base_url="https://docs.prefect.io",
            rate_limit_delay=2.0,  # Be respectful to docs site
            timeout=30,
        )
        self.max_pages = 500  # Limit crawl depth

    async def scrape(self) -> list[dict[str, Any]]:
        """
        Scrape Prefect documentation.

        Returns:
            List of documents with title, URL, category, and content
        """
        if not self.session:
            logger.error("Session not initialized")
            return []

        documents = []
        pages_to_visit = [f"{self.base_url}/latest/"]
        visited = set()

        while pages_to_visit and len(visited) < self.max_pages:
            url = pages_to_visit.pop(0)
            if url in visited:
                continue

            visited.add(url)
            logger.info(f"Scraping {url}")

            content = await self._fetch_page(url)
            if not content:
                continue

            soup = self._parse_html(content)

            # Extract main content
            doc = self._extract_content(soup, url)
            if doc:
                documents.append(doc)

            # Get links to follow
            new_links = self._get_page_links(soup, url)
            for link in new_links:
                if link not in visited and link not in pages_to_visit:
                    pages_to_visit.append(link)

        logger.info(f"Scraped {len(documents)} Prefect documentation pages")
        return documents

    def _extract_content(self, soup: BeautifulSoup, url: str) -> dict[str, Any] | None:
        """Extract content from Prefect docs page."""
        try:
            # Get title
            title_elem = soup.find("h1")
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract main content - Prefect uses specific selectors
            main_content = soup.find("main")
            if not main_content:
                main_content = soup.find("article")
            if not main_content:
                main_content = soup.find("div", {"class": "content"})

            if not main_content:
                logger.warning(f"Could not find main content in {url}")
                return None

            # Remove navigation elements
            for nav in main_content.find_all(["nav", "footer", "aside"]):
                nav.decompose()

            # Extract code examples
            code_blocks = []
            for code in main_content.find_all("pre"):
                code_blocks.append(code.get_text(strip=True))

            # Get clean text content
            content_text = main_content.get_text(separator="\n", strip=True)

            # Categorize based on URL path
            category = self._categorize_page(url)

            return {
                "title": title,
                "url": url,
                "category": category,
                "content": content_text,
                "code_examples": code_blocks,
                "source": "prefect_docs",
            }

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def _get_page_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Extract documentation links from page."""
        links = []

        # Find sidebar navigation (main index)
        sidebar = soup.find("nav", {"class": "sidebar"})
        if sidebar:
            for link in sidebar.find_all("a", href=True):
                href = link["href"]
                if href.startswith("#"):
                    continue
                full_url = urljoin(current_url, href)
                if self._is_allowed_url(full_url):
                    links.append(full_url)

        # Find table of contents
        toc = soup.find("div", {"class": "toc"})
        if toc:
            for link in toc.find_all("a", href=True):
                href = link["href"]
                if href.startswith("#"):
                    continue
                full_url = urljoin(current_url, href)
                if self._is_allowed_url(full_url):
                    links.append(full_url)

        return list(set(links))

    def _categorize_page(self, url: str) -> str:
        """Categorize page based on URL path."""
        if "/guide/" in url:
            return "guide"
        elif "/concepts/" in url:
            return "concepts"
        elif "/api/" in url or "/api-ref/" in url:
            return "api"
        elif "/tutorials/" in url or "/examples/" in url:
            return "tutorial"
        elif "/faq/" in url:
            return "faq"
        else:
            return "general"
