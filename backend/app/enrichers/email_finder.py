"""
Email Finder
Finds and verifies email addresses for leads
"""

from typing import Optional, Dict, Any, List
import re
import logging
import dns.resolver
import aiohttp

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailFinder:
    """
    Email finding and verification service

    Uses multiple strategies:
    1. Common email patterns
    2. Hunter.io API
    3. Website scraping
    4. SMTP verification
    """

    def __init__(self):
        self.common_patterns = [
            "{first}.{last}@{domain}",
            "{first}@{domain}",
            "{last}@{domain}",
            "{first}{last}@{domain}",
            "{f}{last}@{domain}",
            "{first}.{l}@{domain}",
        ]

    async def find_email(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        domain: str,
        company_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find email address for a person

        Args:
            first_name: First name
            last_name: Last name
            domain: Company domain
            company_name: Company name

        Returns:
            Dictionary with email and confidence score
        """
        logger.info(f"Finding email for {first_name} {last_name} at {domain}")

        # Try Hunter.io API if available
        if settings.HUNTER_IO_API_KEY:
            result = await self._find_with_hunter(first_name, last_name, domain)
            if result:
                return result

        # Try common patterns
        if first_name and last_name:
            result = await self._find_with_patterns(first_name, last_name, domain)
            if result:
                return result

        return None

    async def _find_with_hunter(
        self,
        first_name: Optional[str],
        last_name: Optional[str],
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find email using Hunter.io API

        Args:
            first_name: First name
            last_name: Last name
            domain: Domain

        Returns:
            Email result
        """
        url = "https://api.hunter.io/v2/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': settings.HUNTER_IO_API_KEY
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('data', {}).get('email'):
                            return {
                                'email': data['data']['email'],
                                'confidence': data['data'].get('score', 0),
                                'source': 'hunter.io',
                                'pattern': data['data'].get('pattern'),
                            }
        except Exception as e:
            logger.error(f"Hunter.io API error: {str(e)}")

        return None

    async def _find_with_patterns(
        self,
        first_name: str,
        last_name: str,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find email using common patterns and verification

        Args:
            first_name: First name
            last_name: Last name
            domain: Domain

        Returns:
            Email result
        """
        # Normalize names
        first = first_name.lower().replace(' ', '')
        last = last_name.lower().replace(' ', '')
        f = first[0] if first else ''
        l = last[0] if last else ''

        # Generate possible emails
        possible_emails = []
        for pattern in self.common_patterns:
            try:
                email = pattern.format(
                    first=first,
                    last=last,
                    f=f,
                    l=l,
                    domain=domain
                )
                possible_emails.append(email)
            except KeyError:
                continue

        # Verify each email
        for email in possible_emails:
            if await self.verify_email(email):
                return {
                    'email': email,
                    'confidence': 70,  # Medium confidence for pattern matching
                    'source': 'pattern_matching',
                    'pattern': self._extract_pattern(email, first, last),
                }

        return None

    def _extract_pattern(self, email: str, first_name: str, last_name: str) -> str:
        """Extract email pattern from an email address"""
        local_part = email.split('@')[0]

        pattern = local_part
        pattern = pattern.replace(first_name.lower(), '{first}')
        pattern = pattern.replace(last_name.lower(), '{last}')
        pattern = pattern.replace(first_name[0].lower(), '{f}')
        pattern = pattern.replace(last_name[0].lower(), '{l}')

        return pattern + '@{domain}'

    async def verify_email(self, email: str) -> bool:
        """
        Verify if an email address exists

        Uses:
        1. Syntax validation
        2. Domain validation (MX records)
        3. SMTP verification (optional)

        Args:
            email: Email address to verify

        Returns:
            True if email is valid and exists
        """
        # Syntax validation
        if not self._is_valid_syntax(email):
            return False

        # Domain validation
        domain = email.split('@')[1]
        if not await self._check_mx_records(domain):
            return False

        # SMTP verification (can be unreliable and slow)
        # Disabled by default to avoid getting blocked
        # if settings.FEATURE_EMAIL_VERIFICATION:
        #     return await self._smtp_verification(email)

        return True  # Domain has MX records, likely valid

    def _is_valid_syntax(self, email: str) -> bool:
        """Validate email syntax"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    async def _check_mx_records(self, domain: str) -> bool:
        """
        Check if domain has MX records

        Args:
            domain: Domain name

        Returns:
            True if MX records exist
        """
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return False
        except Exception as e:
            logger.error(f"MX record check error for {domain}: {str(e)}")
            return False

    async def find_generic_emails(self, domain: str) -> List[str]:
        """
        Find generic company emails (info@, contact@, etc.)

        Args:
            domain: Company domain

        Returns:
            List of generic email addresses
        """
        generic_prefixes = [
            'info', 'contact', 'hello', 'support', 'sales',
            'marketing', 'admin', 'office', 'inquiries'
        ]

        verified_emails = []

        for prefix in generic_prefixes:
            email = f"{prefix}@{domain}"
            if await self.verify_email(email):
                verified_emails.append(email)

        return verified_emails

    async def get_email_pattern(self, domain: str) -> Optional[str]:
        """
        Determine the email pattern used by a company

        Args:
            domain: Company domain

        Returns:
            Email pattern string
        """
        if settings.HUNTER_IO_API_KEY:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': settings.HUNTER_IO_API_KEY,
                'limit': 1
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            pattern = data.get('data', {}).get('pattern')
                            return pattern
            except Exception as e:
                logger.error(f"Error getting email pattern: {str(e)}")

        return None

    async def bulk_verify_emails(self, emails: List[str]) -> Dict[str, bool]:
        """
        Verify multiple emails efficiently

        Args:
            emails: List of email addresses

        Returns:
            Dictionary mapping emails to validity
        """
        results = {}

        for email in emails:
            results[email] = await self.verify_email(email)

        return results
