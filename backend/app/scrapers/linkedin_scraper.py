"""
LinkedIn Scraper
Scrapes company and people data from LinkedIn
"""

from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import quote_plus

from app.scrapers.base import BaseScraper
from app.core.config import settings

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    """
    LinkedIn scraper for company and contact information

    Note: This scraper requires either:
    1. LinkedIn API credentials (recommended)
    2. Browser automation with login (use cautiously)
    3. Public LinkedIn data only (limited information)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.base_url = "https://www.linkedin.com"
        self.api_base_url = "https://api.linkedin.com/v2"

    async def scrape(
        self,
        search_query: Optional[str] = None,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        company_size: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape LinkedIn companies based on search criteria

        Args:
            search_query: Search keywords
            industry: Industry filter
            location: Location filter
            company_size: Company size filter
            limit: Maximum number of results

        Returns:
            List of company data
        """
        logger.info(f"Starting LinkedIn scrape: query={search_query}, industry={industry}")

        # Check if API credentials are available
        if settings.LINKEDIN_ACCESS_TOKEN:
            return await self._scrape_with_api(
                search_query, industry, location, company_size, limit
            )
        else:
            logger.warning("LinkedIn API credentials not found, using public search")
            return await self._scrape_public(
                search_query, industry, location, company_size, limit
            )

    async def _scrape_with_api(
        self,
        search_query: Optional[str],
        industry: Optional[str],
        location: Optional[str],
        company_size: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape using LinkedIn API (recommended method)

        Args:
            search_query: Search keywords
            industry: Industry filter
            location: Location filter
            company_size: Company size filter
            limit: Maximum results

        Returns:
            List of company data
        """
        headers = {
            'Authorization': f'Bearer {settings.LINKEDIN_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        }

        # Build search parameters
        params = {
            'q': 'search',
            'count': min(limit, 100),
        }

        if search_query:
            params['keywords'] = search_query

        # Note: LinkedIn API has specific endpoints and parameters
        # This is a simplified example - actual implementation would use proper API endpoints

        url = f"{self.api_base_url}/organizations"

        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._parse_api_response(data)
                else:
                    logger.error(f"LinkedIn API error: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"LinkedIn API scraping error: {str(e)}")
            self.errors.append(str(e))
            return []

    async def _scrape_public(
        self,
        search_query: Optional[str],
        industry: Optional[str],
        location: Optional[str],
        company_size: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape public LinkedIn data (limited information)

        Args:
            search_query: Search keywords
            industry: Industry filter
            location: Location filter
            company_size: Company size filter
            limit: Maximum results

        Returns:
            List of company data
        """
        results = []

        # Build search URL
        query_parts = []
        if search_query:
            query_parts.append(search_query)
        if industry:
            query_parts.append(industry)

        query = " ".join(query_parts)
        encoded_query = quote_plus(query)

        # LinkedIn company search URL
        search_url = f"{self.base_url}/search/results/companies/?keywords={encoded_query}"

        # Fetch search results page
        html = await self.fetch_with_browser(search_url)
        if not html:
            logger.error("Failed to fetch LinkedIn search results")
            return []

        # Parse search results
        soup = self.parse_html(html)

        # Extract company cards
        # Note: LinkedIn's HTML structure changes frequently
        # This is a simplified example
        company_cards = soup.select('.search-result__wrapper')

        for card in company_cards[:limit]:
            try:
                company_data = await self._parse_company_card(card)
                if company_data:
                    results.append(company_data)
                    self.results.append(company_data)

                # Rate limiting
                await self.rate_limit_delay()

            except Exception as e:
                logger.error(f"Error parsing company card: {str(e)}")
                self.errors.append(str(e))

        logger.info(f"Scraped {len(results)} companies from LinkedIn")
        return results

    async def _parse_company_card(self, card) -> Optional[Dict[str, Any]]:
        """
        Parse company card from search results

        Args:
            card: BeautifulSoup element

        Returns:
            Company data dictionary
        """
        try:
            company_name = self.extract_text(card, '.entity-result__title-text a')
            company_url = self.extract_attribute(card, '.entity-result__title-text a', 'href')
            tagline = self.extract_text(card, '.entity-result__primary-subtitle')
            location = self.extract_text(card, '.entity-result__secondary-subtitle')
            industry = self.extract_text(card, '.entity-result__summary')

            if not company_name:
                return None

            return {
                'company_name': self.clean_text(company_name),
                'company_website': None,  # Not available in search results
                'linkedin_url': company_url if company_url and company_url.startswith('http') else f"{self.base_url}{company_url}",
                'company_tagline': self.clean_text(tagline),
                'industry': self.clean_text(industry),
                'city': self.clean_text(location),
                'source': 'linkedin',
                'source_url': company_url,
            }

        except Exception as e:
            logger.error(f"Error parsing company card: {str(e)}")
            return None

    async def scrape_company_details(self, company_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed information from a company page

        Args:
            company_url: LinkedIn company page URL

        Returns:
            Detailed company data
        """
        html = await self.fetch_with_browser(company_url)
        if not html:
            return None

        return await self.parse(html)

    async def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse company page HTML

        Args:
            html: HTML content

        Returns:
            Parsed company data
        """
        soup = self.parse_html(html)

        # Extract company information
        # Note: LinkedIn's structure changes frequently
        # This is a simplified example

        company_data = {
            'company_name': self.extract_text(soup, 'h1.org-top-card-summary__title'),
            'company_tagline': self.extract_text(soup, '.org-top-card-summary__tagline'),
            'company_website': self.extract_attribute(soup, 'a[data-tracking-control-name="about_website"]', 'href'),
            'industry': self.extract_text(soup, '.org-page-details__definition:has(.org-page-details__label:-soup-contains("Industry")) dd'),
            'company_size': self.extract_text(soup, '.org-page-details__definition:has(.org-page-details__label:-soup-contains("Company size")) dd'),
            'headquarters': self.extract_text(soup, '.org-page-details__definition:has(.org-page-details__label:-soup-contains("Headquarters")) dd'),
            'founded_year': self.extract_text(soup, '.org-page-details__definition:has(.org-page-details__label:-soup-contains("Founded")) dd'),
            'linkedin_followers': self.extract_text(soup, '.org-top-card-summary-info-list__info-item'),
            'company_description': self.extract_text(soup, '.org-about-us-organization-description__text'),
        }

        # Clean and process employee count
        if company_data.get('company_size'):
            company_data['employee_range'] = company_data['company_size']
            # Extract numeric values
            numbers = re.findall(r'\d+', company_data['company_size'].replace(',', ''))
            if numbers:
                company_data['employee_count'] = int(numbers[0])

        # Extract founded year
        if company_data.get('founded_year'):
            year_match = re.search(r'\d{4}', company_data['founded_year'])
            if year_match:
                company_data['founded_year'] = int(year_match.group())

        return company_data

    async def _parse_api_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse LinkedIn API response

        Args:
            data: API response data

        Returns:
            List of parsed company data
        """
        results = []

        # Parse LinkedIn API structure
        # Actual implementation depends on API endpoint used
        elements = data.get('elements', [])

        for element in elements:
            company_data = {
                'company_name': element.get('name'),
                'company_website': element.get('websiteUrl'),
                'linkedin_url': element.get('vanityName'),
                'industry': element.get('industries', [{}])[0].get('name'),
                'employee_count': element.get('employeeCount'),
                'founded_year': element.get('foundedOn', {}).get('year'),
                'company_description': element.get('description'),
            }

            results.append(company_data)
            self.results.append(company_data)

        return results

    async def search_people(
        self,
        company_name: str,
        job_titles: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search for people (decision makers) at a company

        Args:
            company_name: Company name
            job_titles: List of job titles to search for
            limit: Maximum results

        Returns:
            List of contact data
        """
        if not job_titles:
            job_titles = ['CEO', 'CTO', 'CMO', 'Marketing Director', 'VP Marketing']

        results = []

        for title in job_titles:
            query = f'{title} at {company_name}'
            encoded_query = quote_plus(query)

            search_url = f"{self.base_url}/search/results/people/?keywords={encoded_query}"

            html = await self.fetch_with_browser(search_url)
            if not html:
                continue

            soup = self.parse_html(html)

            # Extract people cards
            people_cards = soup.select('.search-result__wrapper')[:limit]

            for card in people_cards:
                try:
                    person_data = {
                        'contact_name': self.extract_text(card, '.entity-result__title-text a'),
                        'contact_title': self.extract_text(card, '.entity-result__primary-subtitle'),
                        'contact_linkedin': self.extract_attribute(card, '.entity-result__title-text a', 'href'),
                        'company_name': company_name,
                    }

                    if person_data['contact_name']:
                        results.append(person_data)

                    await self.rate_limit_delay()

                except Exception as e:
                    logger.error(f"Error parsing person card: {str(e)}")

        logger.info(f"Found {len(results)} contacts at {company_name}")
        return results
