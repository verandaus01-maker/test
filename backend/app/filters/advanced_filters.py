"""
Advanced Filtering System
Complex filtering engine with 20+ filter types and Boolean logic
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm import Query
from datetime import datetime, timedelta
import logging

from app.models.lead import Lead

logger = logging.getLogger(__name__)


class AdvancedFilter:
    """
    Advanced filtering system for leads with 20+ filter types

    Supports:
    - Industry & sub-industry filtering
    - Geographic targeting (country, state, city, radius-based)
    - Company size (employees, revenue)
    - Technology stack detection
    - Growth signals (hiring, funding, news)
    - Intent signals
    - Custom Boolean queries
    - Date range filtering
    - Lead score filtering
    - And much more!
    """

    def __init__(self, base_query: Query):
        """
        Initialize advanced filter

        Args:
            base_query: Base SQLAlchemy query to apply filters on
        """
        self.query = base_query
        self.filters_applied = []

    def apply_filters(self, filter_config: Dict[str, Any]) -> Query:
        """
        Apply all filters from configuration

        Args:
            filter_config: Dictionary containing filter criteria

        Returns:
            Filtered SQLAlchemy query
        """
        logger.info(f"Applying advanced filters: {list(filter_config.keys())}")

        # Industry filters
        if 'industry' in filter_config:
            self.filter_by_industry(filter_config['industry'])

        if 'sub_industry' in filter_config:
            self.filter_by_sub_industry(filter_config['sub_industry'])

        # Location filters
        if 'location' in filter_config:
            self.filter_by_location(filter_config['location'])

        # Company size filters
        if 'company_size' in filter_config:
            self.filter_by_company_size(filter_config['company_size'])

        if 'revenue' in filter_config:
            self.filter_by_revenue(filter_config['revenue'])

        # Technology filters
        if 'technologies' in filter_config:
            self.filter_by_technologies(filter_config['technologies'])

        if 'tech_categories' in filter_config:
            self.filter_by_tech_categories(filter_config['tech_categories'])

        # Growth signals
        if 'growth_signals' in filter_config:
            self.filter_by_growth_signals(filter_config['growth_signals'])

        # Lead scoring
        if 'lead_score' in filter_config:
            self.filter_by_lead_score(filter_config['lead_score'])

        # Contact information
        if 'has_email' in filter_config:
            self.filter_has_email(filter_config['has_email'])

        if 'email_verified' in filter_config:
            self.filter_email_verified(filter_config['email_verified'])

        if 'has_phone' in filter_config:
            self.filter_has_phone(filter_config['has_phone'])

        # Status filters
        if 'status' in filter_config:
            self.filter_by_status(filter_config['status'])

        # Source filters
        if 'source' in filter_config:
            self.filter_by_source(filter_config['source'])

        # Domain filters
        if 'domains' in filter_config:
            self.filter_by_domains(filter_config['domains'])

        if 'exclude_domains' in filter_config:
            self.exclude_domains(filter_config['exclude_domains'])

        # Keywords
        if 'keywords' in filter_config:
            self.filter_by_keywords(filter_config['keywords'])

        # Date range
        if 'date_range' in filter_config:
            self.filter_by_date_range(filter_config['date_range'])

        # Social media presence
        if 'social_media' in filter_config:
            self.filter_by_social_media(filter_config['social_media'])

        # Funding status
        if 'funding' in filter_config:
            self.filter_by_funding(filter_config['funding'])

        # Founded year
        if 'founded_year' in filter_config:
            self.filter_by_founded_year(filter_config['founded_year'])

        # Enrichment status
        if 'is_enriched' in filter_config:
            self.filter_by_enrichment_status(filter_config['is_enriched'])

        # Duplicates
        if 'exclude_duplicates' in filter_config and filter_config['exclude_duplicates']:
            self.exclude_duplicates()

        # Custom field filters
        if 'custom_fields' in filter_config:
            self.filter_by_custom_fields(filter_config['custom_fields'])

        # Tags
        if 'tags' in filter_config:
            self.filter_by_tags(filter_config['tags'])

        logger.info(f"Applied {len(self.filters_applied)} filters")
        return self.query

    def filter_by_industry(self, industries: List[str]):
        """Filter by industry"""
        if isinstance(industries, str):
            industries = [industries]
        self.query = self.query.filter(Lead.industry.in_(industries))
        self.filters_applied.append(f"Industry: {industries}")

    def filter_by_sub_industry(self, sub_industries: List[str]):
        """Filter by sub-industry"""
        if isinstance(sub_industries, str):
            sub_industries = [sub_industries]
        self.query = self.query.filter(Lead.sub_industry.in_(sub_industries))
        self.filters_applied.append(f"Sub-industry: {sub_industries}")

    def filter_by_location(self, location_config: Dict[str, Any]):
        """
        Filter by location (country, state, city, radius)

        Args:
            location_config: Location configuration
                {
                    'country': 'United States',
                    'states': ['California', 'New York'],
                    'cities': ['San Francisco'],
                    'radius': {'lat': 37.7749, 'lng': -122.4194, 'distance_km': 50}
                }
        """
        conditions = []

        if 'country' in location_config:
            countries = location_config['country']
            if isinstance(countries, str):
                countries = [countries]
            conditions.append(Lead.country.in_(countries))

        if 'states' in location_config:
            states = location_config['states']
            if isinstance(states, str):
                states = [states]
            conditions.append(Lead.state.in_(states))

        if 'cities' in location_config:
            cities = location_config['cities']
            if isinstance(cities, str):
                cities = [cities]
            conditions.append(Lead.city.in_(cities))

        # Radius-based filtering (requires lat/lng)
        if 'radius' in location_config:
            radius = location_config['radius']
            lat, lng, distance_km = radius['lat'], radius['lng'], radius['distance_km']

            # Haversine formula for distance calculation
            # This is an approximate distance calculation
            lat_range = distance_km / 111.0  # 1 degree latitude ≈ 111 km
            lng_range = distance_km / (111.0 * abs(func.cos(func.radians(lat))))

            conditions.append(
                and_(
                    Lead.latitude.between(lat - lat_range, lat + lat_range),
                    Lead.longitude.between(lng - lng_range, lng + lng_range)
                )
            )

        if conditions:
            self.query = self.query.filter(and_(*conditions))
            self.filters_applied.append(f"Location: {location_config}")

    def filter_by_company_size(self, size_config: Dict[str, Any]):
        """
        Filter by company size (employees)

        Args:
            size_config: {'min': 10, 'max': 500}
        """
        conditions = []

        if 'min' in size_config:
            conditions.append(Lead.employee_count >= size_config['min'])

        if 'max' in size_config:
            conditions.append(Lead.employee_count <= size_config['max'])

        if 'ranges' in size_config:
            # e.g., ["1-10", "11-50"]
            self.query = self.query.filter(Lead.employee_range.in_(size_config['ranges']))

        if conditions:
            self.query = self.query.filter(and_(*conditions))
            self.filters_applied.append(f"Company size: {size_config}")

    def filter_by_revenue(self, revenue_config: Dict[str, Any]):
        """
        Filter by revenue

        Args:
            revenue_config: {'min': 1000000, 'max': 10000000}
        """
        conditions = []

        if 'min' in revenue_config:
            conditions.append(Lead.annual_revenue >= revenue_config['min'])

        if 'max' in revenue_config:
            conditions.append(Lead.annual_revenue <= revenue_config['max'])

        if conditions:
            self.query = self.query.filter(and_(*conditions))
            self.filters_applied.append(f"Revenue: {revenue_config}")

    def filter_by_technologies(self, technologies: List[str]):
        """
        Filter by specific technologies used

        Args:
            technologies: List of technology names
        """
        if isinstance(technologies, str):
            technologies = [technologies]

        # JSON contains check
        for tech in technologies:
            self.query = self.query.filter(
                func.json_contains(Lead.technologies, f'"{tech}"')
            )

        self.filters_applied.append(f"Technologies: {technologies}")

    def filter_by_tech_categories(self, categories: List[str]):
        """Filter by technology categories"""
        if isinstance(categories, str):
            categories = [categories]

        for category in categories:
            self.query = self.query.filter(
                func.json_contains(Lead.tech_categories, f'"{category}"')
            )

        self.filters_applied.append(f"Tech categories: {categories}")

    def filter_by_growth_signals(self, growth_config: Dict[str, Any]):
        """
        Filter by growth signals

        Args:
            growth_config: {
                'is_hiring': True,
                'has_funding': True,
                'min_job_openings': 5
            }
        """
        if 'is_hiring' in growth_config and growth_config['is_hiring']:
            self.query = self.query.filter(Lead.is_hiring == True)

        if 'has_funding' in growth_config and growth_config['has_funding']:
            self.query = self.query.filter(Lead.recent_funding == True)

        if 'min_job_openings' in growth_config:
            self.query = self.query.filter(
                Lead.job_openings_count >= growth_config['min_job_openings']
            )

        self.filters_applied.append(f"Growth signals: {growth_config}")

    def filter_by_lead_score(self, score_config: Dict[str, Any]):
        """
        Filter by lead score

        Args:
            score_config: {'min': 70, 'max': 100}
        """
        conditions = []

        if 'min' in score_config:
            conditions.append(Lead.lead_score >= score_config['min'])

        if 'max' in score_config:
            conditions.append(Lead.lead_score <= score_config['max'])

        if conditions:
            self.query = self.query.filter(and_(*conditions))
            self.filters_applied.append(f"Lead score: {score_config}")

    def filter_has_email(self, has_email: bool):
        """Filter leads with or without email"""
        if has_email:
            self.query = self.query.filter(
                or_(Lead.email.isnot(None), Lead.contact_email.isnot(None))
            )
        else:
            self.query = self.query.filter(
                and_(Lead.email.is_(None), Lead.contact_email.is_(None))
            )
        self.filters_applied.append(f"Has email: {has_email}")

    def filter_email_verified(self, verified: bool):
        """Filter by email verification status"""
        self.query = self.query.filter(Lead.email_verified == verified)
        self.filters_applied.append(f"Email verified: {verified}")

    def filter_has_phone(self, has_phone: bool):
        """Filter leads with or without phone"""
        if has_phone:
            self.query = self.query.filter(
                or_(Lead.phone.isnot(None), Lead.contact_phone.isnot(None))
            )
        else:
            self.query = self.query.filter(
                and_(Lead.phone.is_(None), Lead.contact_phone.is_(None))
            )
        self.filters_applied.append(f"Has phone: {has_phone}")

    def filter_by_status(self, statuses: List[str]):
        """Filter by lead status"""
        if isinstance(statuses, str):
            statuses = [statuses]
        self.query = self.query.filter(Lead.status.in_(statuses))
        self.filters_applied.append(f"Status: {statuses}")

    def filter_by_source(self, sources: List[str]):
        """Filter by data source"""
        if isinstance(sources, str):
            sources = [sources]
        self.query = self.query.filter(Lead.source.in_(sources))
        self.filters_applied.append(f"Source: {sources}")

    def filter_by_domains(self, domains: List[str]):
        """Include only specific domains"""
        if isinstance(domains, str):
            domains = [domains]
        self.query = self.query.filter(Lead.company_domain.in_(domains))
        self.filters_applied.append(f"Domains: {domains}")

    def exclude_domains(self, domains: List[str]):
        """Exclude specific domains"""
        if isinstance(domains, str):
            domains = [domains]
        self.query = self.query.filter(~Lead.company_domain.in_(domains))
        self.filters_applied.append(f"Exclude domains: {domains}")

    def filter_by_keywords(self, keywords: List[str]):
        """
        Filter by keywords in company name, description, or keywords field

        Args:
            keywords: List of keywords to search for
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        conditions = []
        for keyword in keywords:
            keyword_conditions = [
                Lead.company_name.ilike(f'%{keyword}%'),
                Lead.company_description.ilike(f'%{keyword}%'),
                Lead.company_tagline.ilike(f'%{keyword}%'),
                func.json_contains(Lead.keywords, f'"{keyword}"')
            ]
            conditions.append(or_(*keyword_conditions))

        if conditions:
            self.query = self.query.filter(or_(*conditions))
            self.filters_applied.append(f"Keywords: {keywords}")

    def filter_by_date_range(self, date_config: Dict[str, Any]):
        """
        Filter by date range

        Args:
            date_config: {
                'field': 'created_at',  # created_at, updated_at, enriched_at
                'start': '2024-01-01',
                'end': '2024-12-31'
            }
        """
        field_name = date_config.get('field', 'created_at')
        field = getattr(Lead, field_name)

        conditions = []

        if 'start' in date_config:
            start_date = datetime.fromisoformat(date_config['start'])
            conditions.append(field >= start_date)

        if 'end' in date_config:
            end_date = datetime.fromisoformat(date_config['end'])
            conditions.append(field <= end_date)

        if 'last_n_days' in date_config:
            days = date_config['last_n_days']
            since_date = datetime.utcnow() - timedelta(days=days)
            conditions.append(field >= since_date)

        if conditions:
            self.query = self.query.filter(and_(*conditions))
            self.filters_applied.append(f"Date range: {date_config}")

    def filter_by_social_media(self, social_config: Dict[str, Any]):
        """
        Filter by social media presence

        Args:
            social_config: {
                'has_linkedin': True,
                'has_facebook': True,
                'min_followers': 1000
            }
        """
        if 'has_linkedin' in social_config and social_config['has_linkedin']:
            self.query = self.query.filter(Lead.linkedin_url.isnot(None))

        if 'has_facebook' in social_config and social_config['has_facebook']:
            self.query = self.query.filter(Lead.facebook_url.isnot(None))

        if 'has_twitter' in social_config and social_config['has_twitter']:
            self.query = self.query.filter(Lead.twitter_url.isnot(None))

        if 'min_followers' in social_config:
            self.query = self.query.filter(
                Lead.linkedin_followers >= social_config['min_followers']
            )

        self.filters_applied.append(f"Social media: {social_config}")

    def filter_by_funding(self, funding_config: Dict[str, Any]):
        """
        Filter by funding status

        Args:
            funding_config: {
                'has_funding': True,
                'min_amount': 1000000,
                'rounds': ['Series A', 'Series B']
            }
        """
        if 'has_funding' in funding_config and funding_config['has_funding']:
            self.query = self.query.filter(Lead.recent_funding == True)

        if 'min_amount' in funding_config:
            self.query = self.query.filter(
                Lead.funding_amount >= funding_config['min_amount']
            )

        if 'rounds' in funding_config:
            rounds = funding_config['rounds']
            if isinstance(rounds, str):
                rounds = [rounds]
            self.query = self.query.filter(Lead.funding_round.in_(rounds))

        self.filters_applied.append(f"Funding: {funding_config}")

    def filter_by_founded_year(self, year_config: Dict[str, Any]):
        """
        Filter by founded year

        Args:
            year_config: {'min': 2000, 'max': 2020}
        """
        conditions = []

        if 'min' in year_config:
            conditions.append(Lead.founded_year >= year_config['min'])

        if 'max' in year_config:
            conditions.append(Lead.founded_year <= year_config['max'])

        if conditions:
            self.query = self.query.filter(and_(*conditions))
            self.filters_applied.append(f"Founded year: {year_config}")

    def filter_by_enrichment_status(self, is_enriched: bool):
        """Filter by enrichment status"""
        self.query = self.query.filter(Lead.is_enriched == is_enriched)
        self.filters_applied.append(f"Is enriched: {is_enriched}")

    def exclude_duplicates(self):
        """Exclude duplicate leads"""
        self.query = self.query.filter(Lead.is_duplicate == False)
        self.filters_applied.append("Exclude duplicates")

    def filter_by_custom_fields(self, custom_config: Dict[str, Any]):
        """
        Filter by custom fields

        Args:
            custom_config: {'field_name': 'value'}
        """
        for field, value in custom_config.items():
            self.query = self.query.filter(
                func.json_extract(Lead.custom_fields, f'$.{field}') == value
            )
        self.filters_applied.append(f"Custom fields: {custom_config}")

    def filter_by_tags(self, tags: List[str]):
        """Filter by tags"""
        if isinstance(tags, str):
            tags = [tags]

        for tag in tags:
            self.query = self.query.filter(
                func.json_contains(Lead.tags, f'"{tag}"')
            )

        self.filters_applied.append(f"Tags: {tags}")

    def get_query(self) -> Query:
        """Get the filtered query"""
        return self.query

    def get_applied_filters(self) -> List[str]:
        """Get list of applied filters"""
        return self.filters_applied


class FilterBuilder:
    """
    Helper class to build filter configurations

    Example:
        filter_config = (FilterBuilder()
            .industry(['Technology', 'Software'])
            .location(country='United States', states=['California'])
            .company_size(min=10, max=500)
            .has_email(True)
            .build())
    """

    def __init__(self):
        self.config = {}

    def industry(self, industries: List[str]):
        """Add industry filter"""
        self.config['industry'] = industries
        return self

    def sub_industry(self, sub_industries: List[str]):
        """Add sub-industry filter"""
        self.config['sub_industry'] = sub_industries
        return self

    def location(self, **kwargs):
        """Add location filter"""
        self.config['location'] = kwargs
        return self

    def company_size(self, min: Optional[int] = None, max: Optional[int] = None):
        """Add company size filter"""
        self.config['company_size'] = {}
        if min is not None:
            self.config['company_size']['min'] = min
        if max is not None:
            self.config['company_size']['max'] = max
        return self

    def technologies(self, tech_list: List[str]):
        """Add technologies filter"""
        self.config['technologies'] = tech_list
        return self

    def lead_score(self, min: Optional[float] = None, max: Optional[float] = None):
        """Add lead score filter"""
        self.config['lead_score'] = {}
        if min is not None:
            self.config['lead_score']['min'] = min
        if max is not None:
            self.config['lead_score']['max'] = max
        return self

    def has_email(self, value: bool = True):
        """Add has email filter"""
        self.config['has_email'] = value
        return self

    def keywords(self, keyword_list: List[str]):
        """Add keywords filter"""
        self.config['keywords'] = keyword_list
        return self

    def growth_signals(self, **kwargs):
        """Add growth signals filter"""
        self.config['growth_signals'] = kwargs
        return self

    def build(self) -> Dict[str, Any]:
        """Build and return the filter configuration"""
        return self.config
