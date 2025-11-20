"""
Business-Specific Scraping Strategies
Customized scraping approaches for different business types and industries
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BusinessType(str, Enum):
    """Business type enumeration"""
    TECHNOLOGY = "technology"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    RETAIL = "retail"
    REAL_ESTATE = "real_estate"
    LEGAL = "legal"
    MANUFACTURING = "manufacturing"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"
    PROFESSIONAL_SERVICES = "professional_services"
    ECOMMERCE = "ecommerce"
    SAAS = "saas"


class BusinessScrapingStrategy:
    """
    Defines scraping strategy for a specific business type

    Each strategy includes:
    - Data extraction schema
    - Priority fields
    - Quality indicators
    - Validation rules
    - Source recommendations
    """

    def __init__(
        self,
        business_type: BusinessType,
        schema: Dict[str, Any],
        priority_fields: List[str],
        quality_indicators: List[str],
        recommended_sources: List[str],
    ):
        self.business_type = business_type
        self.schema = schema
        self.priority_fields = priority_fields
        self.quality_indicators = quality_indicators
        self.recommended_sources = recommended_sources

    def get_extraction_schema(self) -> Dict[str, Any]:
        """Get data extraction schema"""
        return self.schema

    def calculate_lead_quality(self, data: Dict[str, Any]) -> float:
        """
        Calculate lead quality based on business-specific indicators

        Args:
            data: Lead data

        Returns:
            Quality score (0-100)
        """
        score = 0
        max_score = len(self.quality_indicators) * 20

        for indicator in self.quality_indicators:
            if data.get(indicator):
                score += 20

        return min((score / max_score) * 100 if max_score > 0 else 0, 100)


# Technology/SaaS Strategy
TECHNOLOGY_STRATEGY = BusinessScrapingStrategy(
    business_type=BusinessType.TECHNOLOGY,
    schema={
        'company_name': {
            'selectors': ['h1', '.company-name', '[itemprop="name"]'],
            'transform': 'text',
            'required': True
        },
        'company_website': {
            'selectors': ['a[href*="http"]', '[itemprop="url"]'],
            'transform': 'href',
            'required': False
        },
        'tech_stack': {
            'selectors': ['.technology', '.tech-stack', '[data-tech]'],
            'transform': 'text',
            'required': False
        },
        'employee_count': {
            'selectors': ['.employees', '[itemprop="numberOfEmployees"]'],
            'transform': 'text',
            'pattern': r'(\d+)',
            'required': False
        },
        'funding': {
            'selectors': ['.funding', '.investment'],
            'transform': 'text',
            'required': False
        },
        'github_url': {
            'selectors': ['a[href*="github.com"]'],
            'transform': 'href',
            'required': False
        },
        'linkedin_url': {
            'selectors': ['a[href*="linkedin.com/company"]'],
            'transform': 'href',
            'required': False
        },
        'email': {
            'selectors': ['a[href^="mailto:"]', '[itemprop="email"]'],
            'transform': 'href',
            'pattern': r'mailto:(.+)',
            'required': False
        },
        'phone': {
            'selectors': ['a[href^="tel:"]', '[itemprop="telephone"]'],
            'transform': 'href',
            'pattern': r'tel:(.+)',
            'required': False
        },
        'description': {
            'selectors': ['meta[name="description"]', '.description', '[itemprop="description"]'],
            'transform': 'text',
            'required': False
        },
        'founders': {
            'selectors': ['.founders', '.team-founders'],
            'transform': 'text',
            'required': False
        },
        'location': {
            'selectors': ['.location', '[itemprop="address"]', '.office-location'],
            'transform': 'text',
            'required': False
        },
    },
    priority_fields=['tech_stack', 'funding', 'github_url', 'employee_count'],
    quality_indicators=['tech_stack', 'github_url', 'funding', 'email', 'linkedin_url'],
    recommended_sources=['linkedin', 'crunchbase', 'angellist', 'company_website'],
)

# Healthcare Strategy
HEALTHCARE_STRATEGY = BusinessScrapingStrategy(
    business_type=BusinessType.HEALTHCARE,
    schema={
        'company_name': {
            'selectors': ['h1', '.practice-name', '.clinic-name'],
            'transform': 'text',
            'required': True
        },
        'specialties': {
            'selectors': ['.specialties', '.services', '.treatments'],
            'transform': 'text',
            'required': False
        },
        'certifications': {
            'selectors': ['.certifications', '.accreditations'],
            'transform': 'text',
            'required': False
        },
        'insurance_accepted': {
            'selectors': ['.insurance', '.accepted-insurance'],
            'transform': 'text',
            'required': False
        },
        'doctors': {
            'selectors': ['.doctor-name', '.physician'],
            'transform': 'text',
            'required': False
        },
        'address': {
            'selectors': ['.address', '[itemprop="address"]'],
            'transform': 'text',
            'required': True
        },
        'phone': {
            'selectors': ['a[href^="tel:"]', '.phone'],
            'transform': 'text',
            'required': True
        },
        'email': {
            'selectors': ['a[href^="mailto:"]'],
            'transform': 'href',
            'pattern': r'mailto:(.+)',
            'required': False
        },
        'hours': {
            'selectors': ['.hours', '.opening-hours'],
            'transform': 'text',
            'required': False
        },
        'rating': {
            'selectors': ['.rating', '[itemprop="ratingValue"]'],
            'transform': 'text',
            'required': False
        },
    },
    priority_fields=['specialties', 'doctors', 'certifications', 'insurance_accepted'],
    quality_indicators=['phone', 'address', 'specialties', 'certifications', 'email'],
    recommended_sources=['google_maps', 'healthgrades', 'zocdoc', 'company_website'],
)

# E-commerce/Retail Strategy
ECOMMERCE_STRATEGY = BusinessScrapingStrategy(
    business_type=BusinessType.ECOMMERCE,
    schema={
        'company_name': {
            'selectors': ['h1', '.store-name', '.brand-name'],
            'transform': 'text',
            'required': True
        },
        'products': {
            'selectors': ['.product', '.product-name'],
            'transform': 'text',
            'required': False
        },
        'product_categories': {
            'selectors': ['.category', '.department'],
            'transform': 'text',
            'required': False
        },
        'price_range': {
            'selectors': ['.price', '.price-range'],
            'transform': 'text',
            'required': False
        },
        'ecommerce_platform': {
            'selectors': ['meta[content*="Shopify"]', 'meta[content*="WooCommerce"]'],
            'transform': 'attr',
            'attr': 'content',
            'required': False
        },
        'payment_methods': {
            'selectors': ['.payment-methods', '.accepted-payments'],
            'transform': 'text',
            'required': False
        },
        'shipping_info': {
            'selectors': ['.shipping', '.delivery'],
            'transform': 'text',
            'required': False
        },
        'social_media': {
            'selectors': ['a[href*="facebook.com"]', 'a[href*="instagram.com"]'],
            'transform': 'href',
            'required': False
        },
        'email': {
            'selectors': ['a[href^="mailto:"]'],
            'transform': 'href',
            'pattern': r'mailto:(.+)',
            'required': False
        },
        'phone': {
            'selectors': ['a[href^="tel:"]'],
            'transform': 'href',
            'pattern': r'tel:(.+)',
            'required': False
        },
    },
    priority_fields=['products', 'product_categories', 'ecommerce_platform'],
    quality_indicators=['ecommerce_platform', 'products', 'email', 'social_media'],
    recommended_sources=['google_maps', 'company_website', 'amazon', 'shopify_directory'],
)

# Finance/Legal Strategy
FINANCE_STRATEGY = BusinessScrapingStrategy(
    business_type=BusinessType.FINANCE,
    schema={
        'company_name': {
            'selectors': ['h1', '.firm-name'],
            'transform': 'text',
            'required': True
        },
        'licenses': {
            'selectors': ['.licenses', '.certifications', '.registrations'],
            'transform': 'text',
            'required': False
        },
        'services': {
            'selectors': ['.services', '.practice-areas'],
            'transform': 'text',
            'required': False
        },
        'partners': {
            'selectors': ['.partners', '.leadership'],
            'transform': 'text',
            'required': False
        },
        'aum': {  # Assets under management
            'selectors': ['.aum', '.assets'],
            'transform': 'text',
            'required': False
        },
        'compliance': {
            'selectors': ['.compliance', '.regulatory'],
            'transform': 'text',
            'required': False
        },
        'address': {
            'selectors': ['.address', '[itemprop="address"]'],
            'transform': 'text',
            'required': True
        },
        'phone': {
            'selectors': ['a[href^="tel:"]'],
            'transform': 'href',
            'required': True
        },
        'email': {
            'selectors': ['a[href^="mailto:"]'],
            'transform': 'href',
            'pattern': r'mailto:(.+)',
            'required': False
        },
    },
    priority_fields=['licenses', 'services', 'aum', 'compliance'],
    quality_indicators=['licenses', 'compliance', 'address', 'phone', 'email'],
    recommended_sources=['sec.gov', 'finra.org', 'company_website', 'linkedin'],
)

# Real Estate Strategy
REAL_ESTATE_STRATEGY = BusinessScrapingStrategy(
    business_type=BusinessType.REAL_ESTATE,
    schema={
        'company_name': {
            'selectors': ['h1', '.agency-name'],
            'transform': 'text',
            'required': True
        },
        'agents': {
            'selectors': ['.agent', '.realtor'],
            'transform': 'text',
            'required': False
        },
        'properties': {
            'selectors': ['.property', '.listing'],
            'transform': 'text',
            'required': False
        },
        'service_areas': {
            'selectors': ['.service-areas', '.coverage'],
            'transform': 'text',
            'required': False
        },
        'specialization': {
            'selectors': ['.specialization', '.property-types'],
            'transform': 'text',
            'required': False
        },
        'brokerage': {
            'selectors': ['.brokerage', '.affiliated-with'],
            'transform': 'text',
            'required': False
        },
        'address': {
            'selectors': ['.address', '[itemprop="address"]'],
            'transform': 'text',
            'required': False
        },
        'phone': {
            'selectors': ['a[href^="tel:"]'],
            'transform': 'href',
            'required': True
        },
        'email': {
            'selectors': ['a[href^="mailto:"]'],
            'transform': 'href',
            'pattern': r'mailto:(.+)',
            'required': False
        },
    },
    priority_fields=['agents', 'service_areas', 'specialization', 'properties'],
    quality_indicators=['agents', 'properties', 'phone', 'email', 'service_areas'],
    recommended_sources=['zillow', 'realtor.com', 'google_maps', 'company_website'],
)

# Professional Services Strategy
PROFESSIONAL_SERVICES_STRATEGY = BusinessScrapingStrategy(
    business_type=BusinessType.PROFESSIONAL_SERVICES,
    schema={
        'company_name': {
            'selectors': ['h1', '.company-name'],
            'transform': 'text',
            'required': True
        },
        'services': {
            'selectors': ['.services', '.capabilities'],
            'transform': 'text',
            'required': False
        },
        'industries_served': {
            'selectors': ['.industries', '.sectors'],
            'transform': 'text',
            'required': False
        },
        'team_size': {
            'selectors': ['.team-size', '.employees'],
            'transform': 'text',
            'pattern': r'(\d+)',
            'required': False
        },
        'clients': {
            'selectors': ['.clients', '.portfolio'],
            'transform': 'text',
            'required': False
        },
        'case_studies': {
            'selectors': ['.case-study', '.project'],
            'transform': 'text',
            'required': False
        },
        'certifications': {
            'selectors': ['.certifications', '.awards'],
            'transform': 'text',
            'required': False
        },
        'address': {
            'selectors': ['.address', '[itemprop="address"]'],
            'transform': 'text',
            'required': False
        },
        'phone': {
            'selectors': ['a[href^="tel:"]'],
            'transform': 'href',
            'required': False
        },
        'email': {
            'selectors': ['a[href^="mailto:"]'],
            'transform': 'href',
            'pattern': r'mailto:(.+)',
            'required': False
        },
    },
    priority_fields=['services', 'industries_served', 'clients', 'case_studies'],
    quality_indicators=['services', 'clients', 'certifications', 'email', 'phone'],
    recommended_sources=['linkedin', 'clutch.co', 'google_maps', 'company_website'],
)


class BusinessStrategyManager:
    """
    Manages business-specific scraping strategies

    Automatically selects and applies the best strategy for a given business type
    """

    def __init__(self):
        self.strategies = {
            BusinessType.TECHNOLOGY: TECHNOLOGY_STRATEGY,
            BusinessType.SAAS: TECHNOLOGY_STRATEGY,  # Same as tech
            BusinessType.HEALTHCARE: HEALTHCARE_STRATEGY,
            BusinessType.FINANCE: FINANCE_STRATEGY,
            BusinessType.LEGAL: FINANCE_STRATEGY,  # Similar to finance
            BusinessType.RETAIL: ECOMMERCE_STRATEGY,
            BusinessType.ECOMMERCE: ECOMMERCE_STRATEGY,
            BusinessType.REAL_ESTATE: REAL_ESTATE_STRATEGY,
            BusinessType.PROFESSIONAL_SERVICES: PROFESSIONAL_SERVICES_STRATEGY,
            BusinessType.MANUFACTURING: PROFESSIONAL_SERVICES_STRATEGY,
            BusinessType.EDUCATION: PROFESSIONAL_SERVICES_STRATEGY,
            BusinessType.HOSPITALITY: ECOMMERCE_STRATEGY,
        }

    def get_strategy(self, business_type: str) -> BusinessScrapingStrategy:
        """
        Get scraping strategy for business type

        Args:
            business_type: Business type string

        Returns:
            BusinessScrapingStrategy instance
        """
        try:
            bt = BusinessType(business_type.lower())
            return self.strategies.get(bt, PROFESSIONAL_SERVICES_STRATEGY)
        except ValueError:
            logger.warning(f"Unknown business type: {business_type}, using default strategy")
            return PROFESSIONAL_SERVICES_STRATEGY

    def get_extraction_schema(self, business_type: str) -> Dict[str, Any]:
        """Get extraction schema for business type"""
        strategy = self.get_strategy(business_type)
        return strategy.get_extraction_schema()

    def calculate_lead_quality(self, business_type: str, data: Dict[str, Any]) -> float:
        """Calculate lead quality for business type"""
        strategy = self.get_strategy(business_type)
        return strategy.calculate_lead_quality(data)

    def get_recommended_sources(self, business_type: str) -> List[str]:
        """Get recommended data sources for business type"""
        strategy = self.get_strategy(business_type)
        return strategy.recommended_sources

    def auto_detect_business_type(self, data: Dict[str, Any]) -> Optional[BusinessType]:
        """
        Automatically detect business type from scraped data

        Args:
            data: Scraped lead data

        Returns:
            Detected business type or None
        """
        # Keywords that indicate business type
        indicators = {
            BusinessType.TECHNOLOGY: ['software', 'tech', 'saas', 'platform', 'api', 'cloud'],
            BusinessType.HEALTHCARE: ['medical', 'health', 'clinic', 'hospital', 'doctor', 'patient'],
            BusinessType.FINANCE: ['financial', 'investment', 'banking', 'insurance', 'wealth'],
            BusinessType.RETAIL: ['store', 'shop', 'retail', 'boutique'],
            BusinessType.ECOMMERCE: ['online store', 'ecommerce', 'shopify', 'woocommerce'],
            BusinessType.REAL_ESTATE: ['real estate', 'property', 'realtor', 'broker'],
            BusinessType.LEGAL: ['law', 'legal', 'attorney', 'lawyer'],
            BusinessType.PROFESSIONAL_SERVICES: ['consulting', 'agency', 'services', 'solutions'],
        }

        # Combine all text data
        text = ' '.join(str(v).lower() for v in data.values() if v)

        # Score each business type
        scores = {}
        for business_type, keywords in indicators.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[business_type] = score

        # Return highest scoring type
        if scores:
            return max(scores, key=scores.get)

        return None

    def list_available_strategies(self) -> List[str]:
        """List all available business strategies"""
        return [bt.value for bt in BusinessType]


# Global strategy manager instance
strategy_manager = BusinessStrategyManager()
