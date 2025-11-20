"""
Advanced Scraper Engine
Enterprise-grade scraping with anti-detection, smart parsing, and quality control
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import random
import time
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from fake_useragent import UserAgent
import hashlib

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class AdvancedScraperEngine(BaseScraper):
    """
    Advanced scraping engine with:
    - Anti-bot detection evasion
    - Fingerprint randomization
    - Human-like behavior simulation
    - Smart retry logic
    - Content extraction algorithms
    - Quality validation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.user_agent_rotator = UserAgent()
        self.browser_fingerprints = self._generate_fingerprints()
        self.request_delays = []  # Track timing for human-like patterns

    def _generate_fingerprints(self) -> List[Dict[str, Any]]:
        """Generate multiple browser fingerprints for rotation"""
        return [
            {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'platform': 'Win32',
                'languages': ['en-US', 'en'],
            },
            {
                'viewport': {'width': 1440, 'height': 900},
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'platform': 'MacIntel',
                'languages': ['en-US', 'en'],
            },
            {
                'viewport': {'width': 1366, 'height': 768},
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                'platform': 'Linux x86_64',
                'languages': ['en-US', 'en'],
            },
        ]

    async def create_stealth_browser(self) -> tuple[Browser, BrowserContext]:
        """
        Create browser with stealth mode and anti-detection measures

        Returns:
            Tuple of (browser, context)
        """
        playwright = await async_playwright().start()

        # Random fingerprint
        fingerprint = random.choice(self.browser_fingerprints)

        # Launch browser with stealth settings
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                f'--window-size={fingerprint["viewport"]["width"]},{fingerprint["viewport"]["height"]}',
            ]
        )

        # Create context with fingerprint
        context = await browser.new_context(
            viewport=fingerprint['viewport'],
            user_agent=fingerprint['user_agent'],
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'longitude': -74.0060, 'latitude': 40.7128},
            permissions=['geolocation'],
        )

        # Add stealth scripts
        await context.add_init_script("""
            // Override navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });

            // Override chrome property
            window.chrome = {
                runtime: {}
            };

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        return browser, context

    async def human_like_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """
        Implement human-like delays between actions

        Args:
            min_seconds: Minimum delay
            max_seconds: Maximum delay
        """
        delay = random.uniform(min_seconds, max_seconds)
        self.request_delays.append(delay)
        await asyncio.sleep(delay)

    async def simulate_human_behavior(self, page: Page):
        """
        Simulate human browsing behavior

        Args:
            page: Playwright page
        """
        # Random mouse movements
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))

        # Random scrolling
        scroll_amount = random.randint(300, 800)
        await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Scroll back up a bit
        await page.evaluate(f'window.scrollBy(0, -{scroll_amount // 2})')
        await asyncio.sleep(random.uniform(0.3, 0.7))

    async def smart_wait_for_content(self, page: Page, selectors: List[str], timeout: int = 30000):
        """
        Smart waiting for content with multiple selector fallbacks

        Args:
            page: Playwright page
            selectors: List of CSS selectors to try
            timeout: Maximum wait time in ms

        Returns:
            First selector that loaded successfully
        """
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=timeout, state='visible')
                logger.info(f"Content loaded with selector: {selector}")
                return selector
            except Exception as e:
                logger.debug(f"Selector {selector} not found: {str(e)}")
                continue

        raise Exception(f"None of the selectors loaded: {selectors}")

    async def extract_structured_data(self, page: Page, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data using a schema definition

        Args:
            page: Playwright page
            schema: Extraction schema with selectors and transformers

        Returns:
            Extracted data dictionary

        Example schema:
        {
            'company_name': {
                'selectors': ['h1.company-name', '.company-title', 'h1'],
                'transform': 'text',
                'required': True
            },
            'email': {
                'selectors': ['a[href^="mailto:"]'],
                'transform': 'href',
                'pattern': r'mailto:(.+)'
            }
        }
        """
        result = {}
        html = await page.content()
        soup = BeautifulSoup(html, 'lxml')

        for field_name, field_config in schema.items():
            selectors = field_config.get('selectors', [])
            transform = field_config.get('transform', 'text')
            pattern = field_config.get('pattern')
            required = field_config.get('required', False)

            value = None

            # Try each selector
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    element = elements[0]

                    # Apply transformation
                    if transform == 'text':
                        value = element.get_text(strip=True)
                    elif transform == 'href':
                        value = element.get('href')
                    elif transform == 'src':
                        value = element.get('src')
                    elif transform == 'attr':
                        attr_name = field_config.get('attr')
                        value = element.get(attr_name)

                    # Apply pattern extraction
                    if value and pattern:
                        import re
                        match = re.search(pattern, value)
                        if match:
                            value = match.group(1) if match.groups() else match.group(0)

                    if value:
                        break

            # Handle required fields
            if required and not value:
                logger.warning(f"Required field '{field_name}' not found")

            result[field_name] = value

        return result

    async def intelligent_pagination(self, page: Page, max_pages: int = 10) -> List[str]:
        """
        Intelligent pagination detection and navigation

        Args:
            page: Playwright page
            max_pages: Maximum pages to scrape

        Returns:
            List of page URLs
        """
        urls = [page.url]

        pagination_selectors = [
            'a[rel="next"]',
            'a.next',
            'button.next',
            '[aria-label="Next"]',
            'a:has-text("Next")',
            'a:has-text("→")',
            '.pagination a:last-child',
        ]

        for page_num in range(2, max_pages + 1):
            # Try to find next button
            next_button = None
            for selector in pagination_selectors:
                try:
                    next_button = await page.query_selector(selector)
                    if next_button:
                        logger.info(f"Found pagination with selector: {selector}")
                        break
                except:
                    continue

            if not next_button:
                logger.info(f"No more pages found after page {page_num - 1}")
                break

            # Click next and wait
            try:
                await next_button.click()
                await self.human_like_delay(2, 4)
                await page.wait_for_load_state('networkidle', timeout=30000)

                current_url = page.url
                if current_url not in urls:
                    urls.append(current_url)
                    logger.info(f"Navigated to page {page_num}: {current_url}")
                else:
                    logger.info("Reached duplicate URL, stopping pagination")
                    break

            except Exception as e:
                logger.error(f"Error during pagination: {str(e)}")
                break

        return urls

    async def bypass_cloudflare(self, page: Page) -> bool:
        """
        Attempt to bypass Cloudflare protection

        Args:
            page: Playwright page

        Returns:
            True if bypassed successfully
        """
        try:
            # Wait for Cloudflare challenge
            await page.wait_for_selector('#challenge-form', timeout=5000)
            logger.info("Cloudflare challenge detected, waiting...")

            # Wait for challenge to complete
            await page.wait_for_load_state('networkidle', timeout=30000)
            await asyncio.sleep(5)

            # Check if we passed
            if 'cloudflare' not in await page.content().lower():
                logger.info("Cloudflare bypass successful")
                return True

        except:
            # No Cloudflare detected or already bypassed
            return True

        return False

    async def scrape_with_retry(
        self,
        url: str,
        extraction_schema: Dict[str, Any],
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape with intelligent retry logic

        Args:
            url: URL to scrape
            extraction_schema: Data extraction schema
            max_retries: Maximum retry attempts

        Returns:
            Extracted data or None
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping {url} (attempt {attempt + 1}/{max_retries})")

                browser, context = await self.create_stealth_browser()
                page = await context.new_page()

                # Navigate with timeout
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)

                # Bypass protections
                await self.bypass_cloudflare(page)

                # Simulate human behavior
                await self.simulate_human_behavior(page)

                # Wait for content
                await self.human_like_delay(1, 2)

                # Extract data
                data = await self.extract_structured_data(page, extraction_schema)

                await browser.close()

                # Validate data quality
                if self._validate_data_quality(data):
                    logger.info(f"Successfully scraped {url}")
                    return data
                else:
                    logger.warning(f"Data quality check failed for {url}")

            except Exception as e:
                logger.error(f"Scraping attempt {attempt + 1} failed: {str(e)}")
                if browser:
                    await browser.close()

                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)

        return None

    def _validate_data_quality(self, data: Dict[str, Any]) -> bool:
        """
        Validate scraped data quality

        Args:
            data: Scraped data

        Returns:
            True if data meets quality standards
        """
        # Check for minimum required fields
        if not data.get('company_name'):
            return False

        # Check for suspicious patterns
        suspicious_patterns = ['access denied', 'captcha', 'blocked', 'bot detected']
        company_name_lower = str(data.get('company_name', '')).lower()

        for pattern in suspicious_patterns:
            if pattern in company_name_lower:
                return False

        # Check data completeness
        filled_fields = sum(1 for v in data.values() if v)
        completeness_ratio = filled_fields / len(data) if data else 0

        return completeness_ratio >= 0.3  # At least 30% fields filled

    async def batch_scrape_urls(
        self,
        urls: List[str],
        extraction_schema: Dict[str, Any],
        concurrency: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Batch scrape multiple URLs with concurrency control

        Args:
            urls: List of URLs to scrape
            extraction_schema: Data extraction schema
            concurrency: Number of concurrent scrapers

        Returns:
            List of scraped data
        """
        semaphore = asyncio.Semaphore(concurrency)

        async def scrape_with_semaphore(url: str):
            async with semaphore:
                return await self.scrape_with_retry(url, extraction_schema)

        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        valid_results = [r for r in results if r and not isinstance(r, Exception)]

        logger.info(f"Batch scraping completed: {len(valid_results)}/{len(urls)} successful")

        return valid_results

    def calculate_scraping_score(self) -> Dict[str, Any]:
        """
        Calculate scraping performance metrics

        Returns:
            Performance statistics
        """
        stats = self.get_stats()

        avg_delay = sum(self.request_delays) / len(self.request_delays) if self.request_delays else 0

        return {
            **stats,
            'average_delay': round(avg_delay, 2),
            'delays_recorded': len(self.request_delays),
            'human_like_score': self._calculate_human_like_score(),
        }

    def _calculate_human_like_score(self) -> float:
        """
        Calculate how human-like the scraping pattern is

        Returns:
            Score from 0-100
        """
        if not self.request_delays:
            return 0

        # Check delay variance (humans are inconsistent)
        import statistics
        variance = statistics.variance(self.request_delays) if len(self.request_delays) > 1 else 0

        # Higher variance = more human-like
        variance_score = min(variance * 20, 50)

        # Check average delay (humans are slower)
        avg_delay = sum(self.request_delays) / len(self.request_delays)
        delay_score = min(avg_delay * 20, 50)

        return round(variance_score + delay_score, 2)

    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Main scraping method

        Args:
            **kwargs: Scraping parameters

        Returns:
            List of scraped data
        """
        urls = kwargs.get('urls', [])
        schema = kwargs.get('schema', {})
        concurrency = kwargs.get('concurrency', 3)

        return await self.batch_scrape_urls(urls, schema, concurrency)

    async def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML content

        Args:
            html: HTML content

        Returns:
            Parsed data
        """
        soup = BeautifulSoup(html, 'lxml')

        return {
            'title': soup.find('title').get_text() if soup.find('title') else None,
            'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None,
        }
