"""
Google Maps Scraper
Scrapes business information from Google Maps
"""

from typing import List, Dict, Any, Optional
import re
import logging
from urllib.parse import quote_plus
import asyncio

from app.scrapers.base import BaseScraper
from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleMapsScraper(BaseScraper):
    """
    Google Maps scraper for business listings

    Can use:
    1. Google Maps API (recommended - requires API key)
    2. Public scraping (use cautiously, respect rate limits)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.base_url = "https://www.google.com/maps"
        self.api_base_url = "https://maps.googleapis.com/maps/api"

    async def scrape(
        self,
        search_query: str,
        location: Optional[str] = None,
        radius: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Scrape businesses from Google Maps

        Args:
            search_query: Business type or keyword (e.g., "digital marketing agency")
            location: Location to search in
            radius: Search radius in meters
            limit: Maximum number of results

        Returns:
            List of business data
        """
        logger.info(f"Starting Google Maps scrape: query={search_query}, location={location}")

        if settings.GOOGLE_MAPS_API_KEY:
            return await self._scrape_with_api(search_query, location, radius, limit)
        else:
            logger.warning("Google Maps API key not found, using public scraping")
            return await self._scrape_public(search_query, location, limit)

    async def _scrape_with_api(
        self,
        search_query: str,
        location: Optional[str],
        radius: Optional[int],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape using Google Maps Places API

        Args:
            search_query: Search query
            location: Location
            radius: Search radius in meters
            limit: Maximum results

        Returns:
            List of business data
        """
        results = []

        # First, geocode the location if provided
        lat, lng = None, None
        if location:
            geocode_url = f"{self.api_base_url}/geocode/json"
            params = {
                'address': location,
                'key': settings.GOOGLE_MAPS_API_KEY
            }

            try:
                async with self.session.get(geocode_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['status'] == 'OK' and data['results']:
                            location_data = data['results'][0]['geometry']['location']
                            lat, lng = location_data['lat'], location_data['lng']
            except Exception as e:
                logger.error(f"Geocoding error: {str(e)}")

        # Search for places
        search_url = f"{self.api_base_url}/place/textsearch/json"
        params = {
            'query': search_query,
            'key': settings.GOOGLE_MAPS_API_KEY
        }

        if lat and lng:
            params['location'] = f"{lat},{lng}"
            if radius:
                params['radius'] = radius

        next_page_token = None
        collected = 0

        while collected < limit:
            if next_page_token:
                params['pagetoken'] = next_page_token
                # Google requires a delay before using next_page_token
                await asyncio.sleep(2)

            try:
                async with self.session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        if data['status'] == 'OK':
                            places = data.get('results', [])

                            for place in places:
                                if collected >= limit:
                                    break

                                # Get detailed place information
                                place_details = await self._get_place_details(place['place_id'])
                                if place_details:
                                    results.append(place_details)
                                    self.results.append(place_details)
                                    collected += 1

                                await self.rate_limit_delay()

                            # Check for next page
                            next_page_token = data.get('next_page_token')
                            if not next_page_token:
                                break
                        else:
                            logger.error(f"Google Maps API error: {data['status']}")
                            break
                    else:
                        logger.error(f"HTTP error: {response.status}")
                        break

            except Exception as e:
                logger.error(f"Google Maps API scraping error: {str(e)}")
                self.errors.append(str(e))
                break

        logger.info(f"Scraped {len(results)} businesses from Google Maps API")
        return results

    async def _get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed place information

        Args:
            place_id: Google Place ID

        Returns:
            Detailed place data
        """
        details_url = f"{self.api_base_url}/place/details/json"
        params = {
            'place_id': place_id,
            'fields': 'name,formatted_address,geometry,formatted_phone_number,website,'
                     'business_status,opening_hours,rating,user_ratings_total,types,url',
            'key': settings.GOOGLE_MAPS_API_KEY
        }

        try:
            async with self.session.get(details_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['status'] == 'OK':
                        return self._parse_place_details(data['result'])
        except Exception as e:
            logger.error(f"Error getting place details: {str(e)}")

        return None

    def _parse_place_details(self, place: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse place details from API response

        Args:
            place: Place data from API

        Returns:
            Parsed business data
        """
        # Extract address components
        address = place.get('formatted_address', '')
        address_parts = [p.strip() for p in address.split(',')]

        city = address_parts[-2] if len(address_parts) >= 2 else None
        state_zip = address_parts[-1] if len(address_parts) >= 1 else None
        state = None
        postal_code = None

        if state_zip:
            # Extract state and zip code
            parts = state_zip.strip().split()
            if parts:
                state = parts[0]
                if len(parts) > 1:
                    postal_code = parts[1]

        # Get coordinates
        geometry = place.get('geometry', {})
        location = geometry.get('location', {})

        return {
            'company_name': place.get('name'),
            'company_website': place.get('website'),
            'phone': place.get('formatted_phone_number'),
            'address': address,
            'city': city,
            'state': state,
            'postal_code': postal_code,
            'latitude': location.get('lat'),
            'longitude': location.get('lng'),
            'business_type': ', '.join(place.get('types', [])),
            'google_maps_url': place.get('url'),
            'rating': place.get('rating'),
            'reviews_count': place.get('user_ratings_total'),
            'is_open': place.get('business_status') == 'OPERATIONAL',
            'source': 'google_maps',
            'source_url': place.get('url'),
        }

    async def _scrape_public(
        self,
        search_query: str,
        location: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape public Google Maps data (use cautiously)

        Args:
            search_query: Search query
            location: Location
            limit: Maximum results

        Returns:
            List of business data
        """
        results = []

        # Build search query
        query = search_query
        if location:
            query = f"{search_query} in {location}"

        encoded_query = quote_plus(query)
        search_url = f"{self.base_url}/search/{encoded_query}"

        # Fetch search results with browser
        html = await self.fetch_with_browser(search_url)
        if not html:
            logger.error("Failed to fetch Google Maps search results")
            return []

        # Parse results
        soup = self.parse_html(html)

        # Extract business listings
        # Note: Google Maps structure changes frequently
        # This is a simplified example
        business_elements = soup.select('[data-section-id]')

        for element in business_elements[:limit]:
            try:
                business_data = await self._parse_business_element(element)
                if business_data:
                    results.append(business_data)
                    self.results.append(business_data)

                await self.rate_limit_delay()

            except Exception as e:
                logger.error(f"Error parsing business element: {str(e)}")
                self.errors.append(str(e))

        logger.info(f"Scraped {len(results)} businesses from Google Maps")
        return results

    async def _parse_business_element(self, element) -> Optional[Dict[str, Any]]:
        """
        Parse business element from search results

        Args:
            element: BeautifulSoup element

        Returns:
            Business data dictionary
        """
        try:
            # Extract data (structure varies)
            company_name = self.extract_text(element, '.section-result-title')
            address = self.extract_text(element, '.section-result-location')
            phone = self.extract_text(element, '.section-result-phone-number')
            rating = self.extract_text(element, '.section-result-rating')
            business_type = self.extract_text(element, '.section-result-details')

            if not company_name:
                return None

            return {
                'company_name': self.clean_text(company_name),
                'address': self.clean_text(address),
                'phone': self.clean_text(phone),
                'rating': rating,
                'business_type': self.clean_text(business_type),
                'source': 'google_maps',
            }

        except Exception as e:
            logger.error(f"Error parsing business element: {str(e)}")
            return None

    async def parse(self, html: str) -> Dict[str, Any]:
        """
        Parse business page HTML

        Args:
            html: HTML content

        Returns:
            Parsed business data
        """
        soup = self.parse_html(html)

        business_data = {
            'company_name': self.extract_text(soup, 'h1.section-hero-header-title'),
            'rating': self.extract_text(soup, '.section-star-display'),
            'reviews_count': self.extract_text(soup, '.section-rating-term'),
            'business_type': self.extract_text(soup, '.section-rating-term:nth-child(2)'),
            'address': self.extract_text(soup, '[data-section-id="ad"] .section-info-text'),
            'phone': self.extract_text(soup, '[data-section-id="pn0"] .section-info-text'),
            'website': self.extract_attribute(soup, '[data-section-id="ap"] a', 'href'),
        }

        return business_data
