"""
Decision Maker Contact Finder
Finds CEO, Marketing Manager, and key decision-maker contacts
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
import json


class DecisionMakerFinder:
    """
    Find decision-maker contacts (CEO, Marketing Manager, etc.)
    for Indian businesses
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def find_decision_makers(
        self,
        company_name: str,
        website: Optional[str] = None,
        linkedin_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find decision makers for a company
        Returns: CEO, CMO, Marketing Manager, etc. with contact details
        """
        decision_makers = {
            'ceo': None,
            'cmo': None,
            'marketing_manager': None,
            'sales_head': None,
            'founder': None,
            'contacts': [],
        }

        # Strategy 1: LinkedIn company page
        if linkedin_url or company_name:
            linkedin_contacts = await self._find_on_linkedin(company_name, linkedin_url)
            decision_makers['contacts'].extend(linkedin_contacts)

        # Strategy 2: Company website
        if website:
            website_contacts = await self._scrape_company_website(website)
            decision_makers['contacts'].extend(website_contacts)

        # Strategy 3: Email pattern detection
        if website:
            email_patterns = self._generate_email_patterns(company_name, website)
            decision_makers['email_patterns'] = email_patterns

        # Categorize contacts by role
        decision_makers = self._categorize_contacts(decision_makers)

        return decision_makers

    async def _find_on_linkedin(
        self,
        company_name: str,
        linkedin_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find decision makers on LinkedIn"""
        contacts = []

        # LinkedIn People Search API (if available)
        # This would require LinkedIn API access or scraping

        # For now, return structure for manual API integration
        search_titles = [
            'CEO', 'Chief Executive Officer',
            'CMO', 'Chief Marketing Officer',
            'Marketing Manager', 'Marketing Head',
            'Founder', 'Co-Founder',
            'Director', 'Managing Director',
            'Sales Head', 'VP Sales'
        ]

        # Placeholder for LinkedIn integration
        # In production, use LinkedIn Sales Navigator API or similar

        return contacts

    async def _scrape_company_website(self, website: str) -> List[Dict[str, Any]]:
        """Scrape company website for team/contact information"""
        contacts = []

        # Common pages that list team members
        pages_to_check = [
            '/about',
            '/about-us',
            '/team',
            '/our-team',
            '/leadership',
            '/management',
            '/contact',
            '/contact-us',
        ]

        async with aiohttp.ClientSession() as session:
            for page in pages_to_check:
                url = website.rstrip('/') + page

                try:
                    async with session.get(url, headers=self.headers, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            page_contacts = self._parse_team_page(html)
                            contacts.extend(page_contacts)
                except Exception as e:
                    continue

        return contacts

    def _parse_team_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse team/about page for decision maker information"""
        contacts = []
        soup = BeautifulSoup(html, 'html.parser')

        # Look for common patterns
        # Pattern 1: Email addresses
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)

        # Pattern 2: Names with titles
        title_keywords = ['CEO', 'CMO', 'Founder', 'Director', 'Manager', 'Head']

        # Find text blocks containing titles
        all_text = soup.get_text()
        for keyword in title_keywords:
            pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[-–—,]?\s*' + keyword
            matches = re.findall(pattern, all_text)

            for name in matches:
                contacts.append({
                    'name': name,
                    'title': keyword,
                    'source': 'website',
                })

        # Add emails to contacts
        for email in emails:
            # Try to match email with a contact
            name_part = email.split('@')[0]
            contacts.append({
                'email': email,
                'source': 'website',
            })

        return contacts

    def _generate_email_patterns(self, company_name: str, website: str) -> List[str]:
        """
        Generate likely email patterns for decision makers
        Based on common Indian business email formats
        """
        domain = website.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]

        patterns = {
            'CEO': [
                f'ceo@{domain}',
                f'director@{domain}',
                f'md@{domain}',
                f'owner@{domain}',
            ],
            'Marketing': [
                f'marketing@{domain}',
                f'cmo@{domain}',
                f'marketing.manager@{domain}',
                f'mktg@{domain}',
            ],
            'Sales': [
                f'sales@{domain}',
                f'sales.head@{domain}',
                f'business@{domain}',
            ],
            'General': [
                f'info@{domain}',
                f'contact@{domain}',
                f'hello@{domain}',
            ],
        }

        return patterns

    def _categorize_contacts(self, decision_makers: Dict) -> Dict:
        """Categorize contacts by role"""
        contacts = decision_makers.get('contacts', [])

        for contact in contacts:
            title = contact.get('title', '').upper()

            if any(keyword in title for keyword in ['CEO', 'CHIEF EXECUTIVE']):
                decision_makers['ceo'] = contact
            elif any(keyword in title for keyword in ['CMO', 'CHIEF MARKETING', 'MARKETING DIRECTOR']):
                decision_makers['cmo'] = contact
            elif 'MARKETING MANAGER' in title or 'MARKETING HEAD' in title:
                decision_makers['marketing_manager'] = contact
            elif any(keyword in title for keyword in ['SALES HEAD', 'SALES DIRECTOR', 'VP SALES']):
                decision_makers['sales_head'] = contact
            elif 'FOUNDER' in title or 'CO-FOUNDER' in title:
                decision_makers['founder'] = contact

        return decision_makers


class EmailVerifier:
    """Verify if email addresses are valid and deliverable"""

    async def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Verify email address
        Returns: valid, deliverable, risky, role_based
        """
        result = {
            'email': email,
            'valid': False,
            'deliverable': False,
            'risky': False,
            'role_based': False,
            'disposable': False,
        }

        # Basic format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return result

        result['valid'] = True

        # Check if role-based
        role_keywords = ['admin', 'info', 'contact', 'support', 'sales', 'marketing', 'ceo', 'cmo']
        local_part = email.split('@')[0].lower()
        result['role_based'] = any(keyword in local_part for keyword in role_keywords)

        # Check disposable email domains
        disposable_domains = ['tempmail.com', 'guerrillamail.com', '10minutemail.com']
        domain = email.split('@')[1].lower()
        result['disposable'] = domain in disposable_domains

        # In production, use email verification API like:
        # - ZeroBounce
        # - NeverBounce
        # - Hunter.io
        # - Clearout (India-specific)

        return result

    async def bulk_verify_emails(self, emails: List[str]) -> List[Dict[str, Any]]:
        """Verify multiple emails concurrently"""
        tasks = [self.verify_email(email) for email in emails]
        results = await asyncio.gather(*tasks)
        return results


class PhoneFinder:
    """Find phone numbers for decision makers"""

    def extract_phone_numbers(self, text: str, country_code: str = '+91') -> List[str]:
        """
        Extract Indian phone numbers from text
        Handles various formats
        """
        phones = []

        # Indian mobile numbers (10 digits starting with 6-9)
        pattern1 = r'[6-9]\d{9}'

        # With country code
        pattern2 = r'\+91[\s-]?[6-9]\d{9}'

        # With 0 prefix
        pattern3 = r'0[6-9]\d{9}'

        all_patterns = [pattern1, pattern2, pattern3]

        for pattern in all_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up the number
                clean_number = re.sub(r'[\s-]', '', match)
                if clean_number.startswith('0'):
                    clean_number = clean_number[1:]
                if not clean_number.startswith('+'):
                    clean_number = f'+91{clean_number}'

                if clean_number not in phones:
                    phones.append(clean_number)

        return phones

    def format_indian_phone(self, phone: str) -> str:
        """Format Indian phone number consistently"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)

        # If starts with 91, it has country code
        if digits.startswith('91'):
            digits = digits[2:]

        # Should be 10 digits
        if len(digits) == 10:
            return f'+91 {digits[:5]} {digits[5:]}'

        return phone  # Return original if can't format
