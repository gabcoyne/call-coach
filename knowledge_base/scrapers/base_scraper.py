"""
Base scraper class with common functionality for respectful web crawling.
Implements rate limiting, retries, and session management.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for document scrapers."""

    def __init__(
        self,
        base_url: str,
        rate_limit_delay: float = 1.0,
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize base scraper.

        Args:
            base_url: Base URL to scrape from
            rate_limit_delay: Delay between requests in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
        """
        self.base_url = base_url
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: httpx.AsyncClient | None = None
        self.visited_urls: set[str] = set()
        self.last_request_time: float = 0.0

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "User-Agent": "Call-Coach-Documentation-Bot/1.0 (+https://prefect.io/)",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.aclose()

    async def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    async def _fetch_page(self, url: str) -> str | None:
        """
        Fetch a page with retry logic and rate limiting.

        Args:
            url: URL to fetch

        Returns:
            Page content as string, or None if failed
        """
        if url in self.visited_urls or not self._is_allowed_url(url):
            return None

        await self._rate_limit()

        for attempt in range(self.max_retries):
            try:
                if not self.session:
                    raise RuntimeError("Session not initialized")

                response = await self.session.get(url, follow_redirects=True)
                response.raise_for_status()
                self.visited_urls.add(url)
                logger.info(f"Successfully fetched {url}")
                return response.text

            except httpx.HTTPError as e:
                logger.warning(f"Attempt {attempt + 1}/{self.max_retries} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
                    return None

        return None

    def _is_allowed_url(self, url: str) -> bool:
        """Check if URL is allowed to be crawled."""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc and url.startswith(self.base_url)

    def _parse_html(self, content: str) -> BeautifulSoup:
        """Parse HTML content into BeautifulSoup object."""
        return BeautifulSoup(content, "html.parser")

    @abstractmethod
    async def scrape(self) -> list[dict[str, Any]]:
        """
        Main scraping method to be implemented by subclasses.

        Returns:
            List of dictionaries containing scraped content
        """
        pass

    @abstractmethod
    def _extract_content(self, soup: BeautifulSoup, url: str) -> dict[str, Any] | None:
        """Extract relevant content from parsed HTML."""
        pass

    @abstractmethod
    def _get_page_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Get links to follow from current page."""
        pass
