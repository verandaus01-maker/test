"""
India-Specific Lead Scraping System
Supports: Google Maps India, JustDial, IndiaMART, IndiaBizForSale
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import aiohttp
from urllib.parse import quote_plus, urljoin
import json

class IndianBusinessScraper:
    """
    Scraper specifically designed for Indian businesses
    Supports multiple India-specific platforms
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-IN,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }

    async def scrape_google_maps_india(
        self,
        query: str,
        city: str,
        state: str,
        radius_km: int = 10,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape Google Maps for Indian businesses
        Example: "dental clinics in Mumbai, Maharashtra"
        """
        results = []
        search_query = f"{query} in {city}, {state}, India"

        # Google Places API integration
        # Using Places API for accurate Indian business data
        api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

        params = {
            'query': search_query,
            'radius': radius_km * 1000,  # Convert to meters
            'region': 'in',  # India
            'language': 'en',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()

                    for place in data.get('results', [])[:max_results]:
                        business = await self._enrich_google_place(place, session)
                        results.append(business)

        return results

    async def _enrich_google_place(self, place: Dict, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Enrich Google Maps place with additional details"""
        place_id = place.get('place_id')

        # Get detailed information
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {'place_id': place_id, 'fields': 'all'}

        business_data = {
            'company_name': place.get('name'),
            'address': place.get('formatted_address'),
            'phone': None,
            'website': None,
            'rating': place.get('rating'),
            'total_ratings': place.get('user_ratings_total'),
            'business_status': place.get('business_status'),
            'types': place.get('types', []),
            'location': place.get('geometry', {}).get('location'),
            'source': 'Google Maps India',
            'country': 'India',
        }

        try:
            async with session.get(details_url, params=params) as response:
                if response.status == 200:
                    details = await response.json()
                    result = details.get('result', {})

                    business_data.update({
                        'phone': result.get('formatted_phone_number') or result.get('international_phone_number'),
                        'website': result.get('website'),
                        'opening_hours': result.get('opening_hours'),
                        'price_level': result.get('price_level'),
                        'photos': [p.get('photo_reference') for p in result.get('photos', [])[:3]],
                    })
        except Exception as e:
            print(f"Error enriching place: {e}")

        return business_data

    async def scrape_justdial(
        self,
        category: str,
        city: str,
        max_pages: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Scrape JustDial for Indian businesses
        JustDial is India's largest local search engine
        """
        results = []
        base_url = "https://www.justdial.com"

        # Format category and city for JustDial URL
        category_slug = category.lower().replace(' ', '-')
        city_slug = city.lower().replace(' ', '-')

        for page in range(1, max_pages + 1):
            url = f"{base_url}/{city_slug}/{category_slug}/nct-{page}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Parse JustDial listings
                        listings = soup.find_all('li', class_='cntanr')

                        for listing in listings:
                            business = self._parse_justdial_listing(listing, city)
                            if business:
                                results.append(business)

            await asyncio.sleep(2)  # Rate limiting

        return results

    def _parse_justdial_listing(self, listing, city: str) -> Optional[Dict[str, Any]]:
        """Parse individual JustDial listing"""
        try:
            business = {
                'source': 'JustDial',
                'country': 'India',
                'city': city,
            }

            # Company name
            name_elem = listing.find('span', class_='jcn')
            if name_elem:
                business['company_name'] = name_elem.get_text(strip=True)

            # Address
            address_elem = listing.find('span', class_='mrehover')
            if address_elem:
                business['address'] = address_elem.get_text(strip=True)

            # Phone numbers
            phone_elems = listing.find_all('p', class_='contact-info')
            phones = []
            for phone_elem in phone_elems:
                phone_text = phone_elem.get_text(strip=True)
                phone_match = re.findall(r'\d{10}', phone_text)
                phones.extend(phone_match)
            business['phones'] = phones
            business['phone'] = phones[0] if phones else None

            # Rating
            rating_elem = listing.find('span', class_='green-box')
            if rating_elem:
                try:
                    business['rating'] = float(rating_elem.get_text(strip=True))
                except:
                    business['rating'] = None

            # Years in business
            years_elem = listing.find('span', class_='font-10')
            if years_elem and 'yrs' in years_elem.get_text().lower():
                business['years_in_business'] = years_elem.get_text(strip=True)

            return business

        except Exception as e:
            print(f"Error parsing JustDial listing: {e}")
            return None

    async def scrape_indiamart(
        self,
        product_category: str,
        city: str,
        max_results: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Scrape IndiaMART for B2B businesses
        Great for finding manufacturers, suppliers, wholesalers
        """
        results = []
        base_url = "https://www.indiamart.com"
        search_url = f"{base_url}/search.mp"

        params = {
            'ss': product_category,
            'mcatid': '',
            'cityname': city,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Parse IndiaMART results
                    company_cards = soup.find_all('div', class_='c-box')

                    for card in company_cards[:max_results]:
                        business = self._parse_indiamart_listing(card, city)
                        if business:
                            results.append(business)

        return results

    def _parse_indiamart_listing(self, card, city: str) -> Optional[Dict[str, Any]]:
        """Parse IndiaMART company listing"""
        try:
            business = {
                'source': 'IndiaMART',
                'country': 'India',
                'city': city,
            }

            # Company name
            company_elem = card.find('h2', class_='c-name')
            if company_elem:
                business['company_name'] = company_elem.get_text(strip=True)

            # Location
            location_elem = card.find('div', class_='c-add')
            if location_elem:
                business['address'] = location_elem.get_text(strip=True)

            # Business type
            type_elem = card.find('span', class_='c-type')
            if type_elem:
                business['business_type'] = type_elem.get_text(strip=True)

            # GST number (very valuable for Indian businesses)
            gst_elem = card.find('span', class_='gst')
            if gst_elem:
                business['gst_number'] = gst_elem.get_text(strip=True)

            # Year established
            year_elem = card.find('span', class_='year')
            if year_elem:
                business['year_established'] = year_elem.get_text(strip=True)

            # Trust Score (IndiaMART's verification system)
            trust_elem = card.find('div', class_='trust-score')
            if trust_elem:
                business['trust_score'] = trust_elem.get_text(strip=True)

            return business

        except Exception as e:
            print(f"Error parsing IndiaMART listing: {e}")
            return None

    async def find_business_in_radius(
        self,
        business_type: str,
        center_lat: float,
        center_lng: float,
        radius_km: int,
        city: str,
        state: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find businesses within a specific radius
        Perfect for: "Find all dental clinics within 5km of this location"
        """
        results = []

        # Use Google Places Nearby Search
        api_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

        params = {
            'location': f"{center_lat},{center_lng}",
            'radius': radius_km * 1000,
            'type': self._map_business_type_to_google_type(business_type),
            'keyword': business_type,
            'region': 'in',
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()

                    for place in data.get('results', [])[:max_results]:
                        business = await self._enrich_google_place(place, session)
                        business['distance_from_center_km'] = self._calculate_distance(
                            center_lat, center_lng,
                            place['geometry']['location']['lat'],
                            place['geometry']['location']['lng']
                        )
                        results.append(business)

        # Sort by distance
        results.sort(key=lambda x: x.get('distance_from_center_km', 999))

        return results

    def _map_business_type_to_google_type(self, business_type: str) -> str:
        """Map common business types to Google Places types"""
        mapping = {
            'dental': 'dentist',
            'dental clinic': 'dentist',
            'dentist': 'dentist',
            'restaurant': 'restaurant',
            'hotel': 'lodging',
            'gym': 'gym',
            'salon': 'beauty_salon',
            'spa': 'spa',
            'doctor': 'doctor',
            'hospital': 'hospital',
            'pharmacy': 'pharmacy',
            'lawyer': 'lawyer',
            'accountant': 'accountant',
            'real estate': 'real_estate_agency',
            'school': 'school',
            'college': 'university',
        }

        business_lower = business_type.lower()
        for key, value in mapping.items():
            if key in business_lower:
                return value

        return 'establishment'

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c


class IndianCitiesDatabase:
    """Database of major Indian cities with coordinates"""

    CITIES = {
        'Mumbai': {'lat': 19.0760, 'lng': 72.8777, 'state': 'Maharashtra'},
        'Delhi': {'lat': 28.7041, 'lng': 77.1025, 'state': 'Delhi'},
        'Bangalore': {'lat': 12.9716, 'lng': 77.5946, 'state': 'Karnataka'},
        'Hyderabad': {'lat': 17.3850, 'lng': 78.4867, 'state': 'Telangana'},
        'Chennai': {'lat': 13.0827, 'lng': 80.2707, 'state': 'Tamil Nadu'},
        'Kolkata': {'lat': 22.5726, 'lng': 88.3639, 'state': 'West Bengal'},
        'Pune': {'lat': 18.5204, 'lng': 73.8567, 'state': 'Maharashtra'},
        'Ahmedabad': {'lat': 23.0225, 'lng': 72.5714, 'state': 'Gujarat'},
        'Surat': {'lat': 21.1702, 'lng': 72.8311, 'state': 'Gujarat'},
        'Jaipur': {'lat': 26.9124, 'lng': 75.7873, 'state': 'Rajasthan'},
        'Lucknow': {'lat': 26.8467, 'lng': 80.9462, 'state': 'Uttar Pradesh'},
        'Kanpur': {'lat': 26.4499, 'lng': 80.3319, 'state': 'Uttar Pradesh'},
        'Nagpur': {'lat': 21.1458, 'lng': 79.0882, 'state': 'Maharashtra'},
        'Indore': {'lat': 22.7196, 'lng': 75.8577, 'state': 'Madhya Pradesh'},
        'Thane': {'lat': 19.2183, 'lng': 72.9781, 'state': 'Maharashtra'},
        'Bhopal': {'lat': 23.2599, 'lng': 77.4126, 'state': 'Madhya Pradesh'},
        'Visakhapatnam': {'lat': 17.6869, 'lng': 83.2185, 'state': 'Andhra Pradesh'},
        'Vadodara': {'lat': 22.3072, 'lng': 73.1812, 'state': 'Gujarat'},
        'Ghaziabad': {'lat': 28.6692, 'lng': 77.4538, 'state': 'Uttar Pradesh'},
        'Ludhiana': {'lat': 30.9010, 'lng': 75.8573, 'state': 'Punjab'},
        'Agra': {'lat': 27.1767, 'lng': 78.0081, 'state': 'Uttar Pradesh'},
        'Nashik': {'lat': 19.9975, 'lng': 73.7898, 'state': 'Maharashtra'},
        'Faridabad': {'lat': 28.4089, 'lng': 77.3178, 'state': 'Haryana'},
        'Meerut': {'lat': 28.9845, 'lng': 77.7064, 'state': 'Uttar Pradesh'},
        'Rajkot': {'lat': 22.3039, 'lng': 70.8022, 'state': 'Gujarat'},
        'Kalyan-Dombivli': {'lat': 19.2403, 'lng': 73.1305, 'state': 'Maharashtra'},
        'Vasai-Virar': {'lat': 19.4612, 'lng': 72.7932, 'state': 'Maharashtra'},
        'Varanasi': {'lat': 25.3176, 'lng': 82.9739, 'state': 'Uttar Pradesh'},
        'Srinagar': {'lat': 34.0837, 'lng': 74.7973, 'state': 'Jammu and Kashmir'},
        'Aurangabad': {'lat': 19.8762, 'lng': 75.3433, 'state': 'Maharashtra'},
        'Dhanbad': {'lat': 23.7957, 'lng': 86.4304, 'state': 'Jharkhand'},
        'Amritsar': {'lat': 31.6340, 'lng': 74.8723, 'state': 'Punjab'},
        'Navi Mumbai': {'lat': 19.0330, 'lng': 73.0297, 'state': 'Maharashtra'},
        'Allahabad': {'lat': 25.4358, 'lng': 81.8463, 'state': 'Uttar Pradesh'},
        'Ranchi': {'lat': 23.3441, 'lng': 85.3096, 'state': 'Jharkhand'},
        'Howrah': {'lat': 22.5958, 'lng': 88.2636, 'state': 'West Bengal'},
        'Coimbatore': {'lat': 11.0168, 'lng': 76.9558, 'state': 'Tamil Nadu'},
        'Jabalpur': {'lat': 23.1815, 'lng': 79.9864, 'state': 'Madhya Pradesh'},
        'Gwalior': {'lat': 26.2183, 'lng': 78.1828, 'state': 'Madhya Pradesh'},
        'Vijayawada': {'lat': 16.5062, 'lng': 80.6480, 'state': 'Andhra Pradesh'},
        'Jodhpur': {'lat': 26.2389, 'lng': 73.0243, 'state': 'Rajasthan'},
        'Madurai': {'lat': 9.9252, 'lng': 78.1198, 'state': 'Tamil Nadu'},
        'Raipur': {'lat': 21.2514, 'lng': 81.6296, 'state': 'Chhattisgarh'},
        'Kota': {'lat': 25.2138, 'lng': 75.8648, 'state': 'Rajasthan'},
        'Chandigarh': {'lat': 30.7333, 'lng': 76.7794, 'state': 'Chandigarh'},
        'Guwahati': {'lat': 26.1445, 'lng': 91.7362, 'state': 'Assam'},
        'Solapur': {'lat': 17.6599, 'lng': 75.9064, 'state': 'Maharashtra'},
        'Hubli-Dharwad': {'lat': 15.3647, 'lng': 75.1240, 'state': 'Karnataka'},
        'Mysore': {'lat': 12.2958, 'lng': 76.6394, 'state': 'Karnataka'},
        'Tiruchirappalli': {'lat': 10.7905, 'lng': 78.7047, 'state': 'Tamil Nadu'},
        'Bareilly': {'lat': 28.3670, 'lng': 79.4304, 'state': 'Uttar Pradesh'},
    }

    @classmethod
    def get_city_info(cls, city_name: str) -> Optional[Dict[str, Any]]:
        """Get coordinates and state for a city"""
        return cls.CITIES.get(city_name)

    @classmethod
    def search_city(cls, query: str) -> List[str]:
        """Search for cities matching query"""
        query_lower = query.lower()
        return [city for city in cls.CITIES.keys() if query_lower in city.lower()]
