"""
Website Scraper
Scrapes information directly from company websites
Detects technology stack, contact information, and company details
"""

from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import urljoin, urlparse
import asyncio

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class WebsiteScraper(BaseScraper):
    """
    Company website scraper

    Extracts:
    - Company information
    - Contact details
    - Technology stack
    - Social media links
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        self.phone_pattern = re.compile(
            r'(?:\+?(\d{1,3}))?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        )

    async def scrape(
        self,
        websites: List[str],
        scrape_contacts: bool = True,
        detect_tech: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Scrape information from company websites

        Args:
            websites: List of website URLs
            scrape_contacts: Whether to scrape contact information
            detect_tech: Whether to detect technology stack

        Returns:
            List of scraped website data
        """
        logger.info(f"Starting website scraping for {len(websites)} sites")

        tasks = []
        for url in websites:
            tasks.append(self.scrape_website(url, scrape_contacts, detect_tech))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and None values
        valid_results = [r for r in results if r and not isinstance(r, Exception)]

        logger.info(f"Successfully scraped {len(valid_results)}/{len(websites)} websites")
        return valid_results

    async def scrape_website(
        self,
        url: str,
        scrape_contacts: bool = True,
        detect_tech: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Scrape a single website

        Args:
            url: Website URL
            scrape_contacts: Whether to scrape contact information
            detect_tech: Whether to detect technology stack

        Returns:
            Website data dictionary
        """
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        try:
            # Fetch homepage
            html = await self.fetch_with_browser(url)
            if not html:
                return None

            # Parse website data
            website_data = await self.parse(html)
            website_data['company_website'] = url
            website_data['company_domain'] = self.extract_domain(url)
            website_data['source'] = 'company_website'
            website_data['source_url'] = url

            # Scrape contact page if enabled
            if scrape_contacts:
                contacts = await self._scrape_contact_page(url)
                if contacts:
                    website_data.update(contacts)

            # Detect technology stack if enabled
            if detect_tech:
                technologies = await self._detect_technologies(html, url)
                website_data['technologies'] = technologies

            self.results.append(website_data)
            return website_data

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            self.errors.append(f"{url}: {str(e)}")
            return None

    async def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse website HTML

        Args:
            html: HTML content

        Returns:
            Parsed website data
        """
        soup = self.parse_html(html)

        # Extract meta information
        company_data = {
            'company_name': self._extract_company_name(soup),
            'company_description': self._extract_description(soup),
            'company_tagline': self._extract_tagline(soup),
        }

        # Extract emails from page
        emails = self.email_pattern.findall(html)
        if emails:
            # Filter out common non-contact emails
            filtered_emails = [
                e for e in emails
                if not any(x in e.lower() for x in ['noreply', 'example', 'test', 'placeholder'])
            ]
            if filtered_emails:
                company_data['email'] = filtered_emails[0]
                company_data['additional_emails'] = filtered_emails[1:5] if len(filtered_emails) > 1 else []

        # Extract phone numbers
        phones = self.phone_pattern.findall(html)
        if phones:
            company_data['phone'] = phones[0] if phones else None

        # Extract social media links
        social_links = self._extract_social_media(soup)
        company_data.update(social_links)

        return company_data

    def _extract_company_name(self, soup) -> Optional[str]:
        """Extract company name from various sources"""
        # Try meta tags
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name:
            return og_site_name.get('content')

        # Try title tag
        title = soup.find('title')
        if title:
            return title.get_text().split('|')[0].strip()

        # Try header logo alt text
        logo = soup.find('img', class_=re.compile(r'logo', re.I))
        if logo and logo.get('alt'):
            return logo.get('alt')

        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        return None

    def _extract_description(self, soup) -> Optional[str]:
        """Extract company description"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content')

        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content')

        # Try first paragraph in main/about section
        about_section = soup.find(['section', 'div'], class_=re.compile(r'about', re.I))
        if about_section:
            p = about_section.find('p')
            if p:
                return p.get_text(strip=True)

        return None

    def _extract_tagline(self, soup) -> Optional[str]:
        """Extract company tagline"""
        # Look for common tagline classes/elements
        tagline_selectors = [
            '.tagline',
            '.slogan',
            '.subtitle',
            'p.lead',
            '.hero-subtitle'
        ]

        for selector in tagline_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return None

    def _extract_social_media(self, soup) -> Dict[str, Optional[str]]:
        """Extract social media links"""
        social_links = {
            'linkedin_url': None,
            'facebook_url': None,
            'twitter_url': None,
            'instagram_url': None,
            'youtube_url': None,
        }

        # Find all links
        links = soup.find_all('a', href=True)

        for link in links:
            href = link.get('href', '').lower()

            if 'linkedin.com' in href and not social_links['linkedin_url']:
                social_links['linkedin_url'] = link.get('href')
            elif 'facebook.com' in href and not social_links['facebook_url']:
                social_links['facebook_url'] = link.get('href')
            elif 'twitter.com' in href and not social_links['twitter_url']:
                social_links['twitter_url'] = link.get('href')
            elif 'instagram.com' in href and not social_links['instagram_url']:
                social_links['instagram_url'] = link.get('href')
            elif 'youtube.com' in href and not social_links['youtube_url']:
                social_links['youtube_url'] = link.get('href')

        return social_links

    async def _scrape_contact_page(self, base_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape contact page for additional information

        Args:
            base_url: Website base URL

        Returns:
            Contact information dictionary
        """
        # Common contact page URLs
        contact_paths = [
            '/contact',
            '/contact-us',
            '/about/contact',
            '/get-in-touch',
            '/reach-us'
        ]

        for path in contact_paths:
            contact_url = urljoin(base_url, path)

            try:
                html = await self.fetch_html(contact_url)
                if not html:
                    continue

                soup = self.parse_html(html)

                # Extract emails
                emails = self.email_pattern.findall(html)

                # Extract phones
                phones = self.phone_pattern.findall(html)

                # Extract address
                address = self._extract_address(soup)

                if emails or phones or address:
                    return {
                        'contact_email': emails[0] if emails else None,
                        'contact_phone': phones[0] if phones else None,
                        'address': address,
                    }

            except Exception as e:
                logger.debug(f"Error scraping contact page {contact_url}: {str(e)}")
                continue

        return None

    def _extract_address(self, soup) -> Optional[str]:
        """Extract physical address"""
        # Look for address tags
        address_tag = soup.find('address')
        if address_tag:
            return address_tag.get_text(strip=True)

        # Look for common address classes
        address_selectors = [
            '[itemprop="address"]',
            '.address',
            '.location',
            '.office-address'
        ]

        for selector in address_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return None

    async def _detect_technologies(self, html: str, url: str) -> List[str]:
        """
        Detect technologies used on the website

        Args:
            html: HTML content
            url: Website URL

        Returns:
            List of detected technologies
        """
        technologies = set()

        # Check for common technologies in HTML
        tech_patterns = {
            'WordPress': [r'wp-content', r'wp-includes'],
            'Shopify': [r'cdn\.shopify\.com', r'Shopify\.'],
            'Wix': [r'wix\.com', r'parastorage'],
            'Squarespace': [r'squarespace'],
            'React': [r'react', r'__REACT'],
            'Vue.js': [r'vue\.js', r'__VUE__'],
            'Angular': [r'ng-', r'angular'],
            'jQuery': [r'jquery'],
            'Google Analytics': [r'google-analytics\.com', r'gtag'],
            'Google Tag Manager': [r'googletagmanager\.com'],
            'HubSpot': [r'hubspot', r'hs-scripts'],
            'Salesforce': [r'salesforce'],
            'Mailchimp': [r'mailchimp'],
            'Stripe': [r'stripe\.com'],
            'PayPal': [r'paypal\.com'],
            'Cloudflare': [r'cloudflare'],
            'AWS': [r'amazonaws\.com'],
        }

        html_lower = html.lower()

        for tech, patterns in tech_patterns.items():
            for pattern in patterns:
                if re.search(pattern, html_lower, re.IGNORECASE):
                    technologies.add(tech)
                    break

        # Check response headers (would need to fetch separately)
        # This is a simplified version

        return list(technologies)

    async def scrape_about_page(self, base_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape about page for company information

        Args:
            base_url: Website base URL

        Returns:
            Company information
        """
        about_paths = ['/about', '/about-us', '/company', '/who-we-are']

        for path in about_paths:
            about_url = urljoin(base_url, path)

            try:
                html = await self.fetch_html(about_url)
                if not html:
                    continue

                soup = self.parse_html(html)

                # Extract company story/description
                description_elements = soup.select('p')
                if description_elements:
                    paragraphs = [p.get_text(strip=True) for p in description_elements[:3]]
                    description = ' '.join(paragraphs)

                    return {
                        'company_description': description,
                        'about_page_url': about_url
                    }

            except Exception as e:
                logger.debug(f"Error scraping about page {about_url}: {str(e)}")
                continue

        return None
