"""
Scraper for Prefect Horizon documentation.
Extracts features, configuration, and deployment information.
"""
import logging
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class HorizonDocsScraper(BaseScraper):
    """Scrapes Prefect Horizon documentation."""

    def __init__(self):
        super().__init__(
            base_url="https://docs.prefect.io/3.0/cloud/",
            rate_limit_delay=2.0,
            timeout=30,
        )
        self.max_pages = 300

    async def scrape(self) -> list[dict[str, Any]]:
        """
        Scrape Horizon documentation.

        Returns:
            List of documents with title, URL, category, and content
        """
        if not self.session:
            logger.error("Session not initialized")
            return []

        documents = []
        pages_to_visit = [f"{self.base_url}"]
        visited = set()

        while pages_to_visit and len(visited) < self.max_pages:
            url = pages_to_visit.pop(0)
            if url in visited:
                continue

            visited.add(url)
            logger.info(f"Scraping Horizon page: {url}")

            content = await self._fetch_page(url)
            if not content:
                continue

            soup = self._parse_html(content)

            # Extract content
            doc = self._extract_content(soup, url)
            if doc:
                documents.append(doc)

            # Get links to follow
            new_links = self._get_page_links(soup, url)
            for link in new_links:
                if link not in visited and link not in pages_to_visit:
                    pages_to_visit.append(link)

        logger.info(f"Scraped {len(documents)} Horizon documentation pages")
        return documents

    def _extract_content(self, soup: BeautifulSoup, url: str) -> dict[str, Any] | None:
        """Extract content from Horizon docs page."""
        try:
            # Get title
            title_elem = soup.find("h1")
            if not title_elem:
                return None
            title = title_elem.get_text(strip=True)

            # Extract main content
            main_content = soup.find("main")
            if not main_content:
                main_content = soup.find("article")
            if not main_content:
                main_content = soup.find("div", {"class": "content"})

            if not main_content:
                logger.warning(f"Could not find main content in {url}")
                return None

            # Remove navigation, footer, and other noise
            for element in main_content.find_all(["nav", "footer", "aside"]):
                element.decompose()

            # Extract code examples
            code_blocks = []
            for code in main_content.find_all("pre"):
                code_blocks.append(code.get_text(strip=True))

            # Extract configuration details
            config_blocks = []
            for example in main_content.find_all("div", {"class": "highlight"}):
                config_blocks.append(example.get_text(strip=True))

            # Get clean text
            content_text = main_content.get_text(separator="\n", strip=True)

            # Categorize based on URL
            category = self._categorize_page(url)

            return {
                "title": title,
                "url": url,
                "category": category,
                "content": content_text,
                "code_examples": code_blocks,
                "config_examples": config_blocks,
                "source": "horizon_docs",
                "product": "horizon",
            }

        except Exception as e:
            logger.error(f"Error extracting Horizon content from {url}: {e}")
            return None

    def _get_page_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Extract documentation links from Horizon page."""
        links = []

        # Find sidebar navigation
        sidebar = soup.find("nav", {"class": "sidebar"})
        if sidebar:
            for link in sidebar.find_all("a", href=True):
                href = link["href"]
                if href.startswith("#"):
                    continue
                full_url = urljoin(current_url, href)
                if self._is_allowed_url(full_url):
                    links.append(full_url)

        # Find in-page links
        main = soup.find("main")
        if main:
            for link in main.find_all("a", href=True):
                href = link["href"]
                if href.startswith("#"):
                    continue
                full_url = urljoin(current_url, href)
                if self._is_allowed_url(full_url) and "/cloud/" in full_url:
                    links.append(full_url)

        return list(set(links))

    def _categorize_page(self, url: str) -> str:
        """Categorize Horizon page based on URL."""
        if "/account/" in url:
            return "account_management"
        elif "/api/" in url:
            return "api"
        elif "/configuration/" in url or "/config/" in url:
            return "configuration"
        elif "/deployment/" in url:
            return "deployment"
        elif "/auth/" in url or "/security/" in url:
            return "authentication"
        elif "/integrations/" in url:
            return "integrations"
        else:
            return "overview"
