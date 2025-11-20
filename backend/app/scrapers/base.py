"""
Base Scraper Class
Abstract base class for all scrapers with common functionality
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
from fake_useragent import UserAgent
import logging
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Abstract base scraper class

    All scrapers should inherit from this class and implement:
    - scrape() method
    - parse() method
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base scraper

        Args:
            config: Configuration dictionary for the scraper
        """
        self.config = config or {}
        self.user_agent = UserAgent()
        self.session: Optional[aiohttp.ClientSession] = None
        self.browser: Optional[Browser] = None
        self.results: List[Dict[str, Any]] = []
        self.errors: List[str] = []

    async def __aenter__(self):
        """Async context manager entry"""
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()

    async def setup(self):
        """Setup scraper resources"""
        # Create HTTP session
        self.session = aiohttp.ClientSession(
            headers=self._get_headers(),
            timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
        )
        logger.info(f"{self.__class__.__name__} initialized")

    async def cleanup(self):
        """Cleanup scraper resources"""
        if self.session:
            await self.session.close()
        if self.browser:
            await self.browser.close()
        logger.info(f"{self.__class__.__name__} cleaned up")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for requests

        Returns:
            Dictionary of HTTP headers
        """
        return {
            'User-Agent': self.user_agent.random if not settings.USER_AGENT else settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def _get_proxy(self) -> Optional[str]:
        """
        Get proxy URL if proxy rotation is enabled

        Returns:
            Proxy URL or None
        """
        if settings.PROXY_ENABLED and settings.PROXY_ROTATION_URL:
            return settings.PROXY_ROTATION_URL
        return None

    async def fetch_html(self, url: str, retry: int = 0) -> Optional[str]:
        """
        Fetch HTML content from URL

        Args:
            url: URL to fetch
            retry: Current retry attempt

        Returns:
            HTML content or None if failed
        """
        if retry >= settings.MAX_RETRIES:
            logger.error(f"Max retries reached for {url}")
            return None

        try:
            proxy = await self._get_proxy()
            async with self.session.get(url, proxy=proxy) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:  # Too Many Requests
                    logger.warning(f"Rate limited on {url}, waiting...")
                    await asyncio.sleep(5 * (retry + 1))
                    return await self.fetch_html(url, retry + 1)
                else:
                    logger.error(f"HTTP {response.status} for {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            await asyncio.sleep(2 * (retry + 1))
            return await self.fetch_html(url, retry + 1)
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            self.errors.append(f"Fetch error for {url}: {str(e)}")
            return None

    async def fetch_with_browser(self, url: str) -> Optional[str]:
        """
        Fetch HTML using headless browser (for JavaScript-heavy sites)

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=True)
                context = await self.browser.new_context(
                    user_agent=self.user_agent.random,
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()

                # Navigate to URL
                await page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait for content to load
                await asyncio.sleep(2)

                # Get HTML content
                content = await page.content()

                await self.browser.close()
                self.browser = None

                return content

        except Exception as e:
            logger.error(f"Browser fetch error for {url}: {str(e)}")
            self.errors.append(f"Browser fetch error for {url}: {str(e)}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content with BeautifulSoup

        Args:
            html: HTML content

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')

    async def rate_limit_delay(self):
        """Apply rate limiting delay"""
        delay = self.config.get('rate_limit_delay', settings.REQUEST_TIMEOUT)
        await asyncio.sleep(delay)

    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text from BeautifulSoup using CSS selector

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            Extracted text or None
        """
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        return None

    def extract_attribute(
        self,
        soup: BeautifulSoup,
        selector: str,
        attribute: str
    ) -> Optional[str]:
        """
        Extract attribute from element

        Args:
            soup: BeautifulSoup object
            selector: CSS selector
            attribute: Attribute name

        Returns:
            Attribute value or None
        """
        element = soup.select_one(selector)
        if element:
            return element.get(attribute)
        return None

    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean and normalize text

        Args:
            text: Text to clean

        Returns:
            Cleaned text or None
        """
        if not text:
            return None
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL

        Args:
            url: URL string

        Returns:
            Domain name or None
        """
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return None

    @abstractmethod
    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Main scraping method - must be implemented by subclasses

        Returns:
            List of scraped data dictionaries
        """
        pass

    @abstractmethod
    async def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML and extract data - must be implemented by subclasses

        Args:
            html: HTML content

        Returns:
            Parsed data dictionary
        """
        pass

    def get_results(self) -> List[Dict[str, Any]]:
        """
        Get scraping results

        Returns:
            List of scraped results
        """
        return self.results

    def get_errors(self) -> List[str]:
        """
        Get scraping errors

        Returns:
            List of error messages
        """
        return self.errors

    def get_stats(self) -> Dict[str, Any]:
        """
        Get scraping statistics

        Returns:
            Statistics dictionary
        """
        return {
            'total_results': len(self.results),
            'total_errors': len(self.errors),
            'success_rate': (len(self.results) / (len(self.results) + len(self.errors)) * 100)
                if (len(self.results) + len(self.errors)) > 0 else 0
        }
