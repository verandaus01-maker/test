"""
Automatic Website Audit System
Analyzes websites and generates improvement suggestions as lead magnets
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
from datetime import datetime


class WebsiteAuditor:
    """
    Comprehensive website audit system
    Generates detailed reports as lead magnets for outreach
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def audit_website(self, url: str) -> Dict[str, Any]:
        """
        Complete website audit
        Returns comprehensive analysis with scores and recommendations
        """
        audit_result = {
            'url': url,
            'audited_at': datetime.utcnow().isoformat(),
            'overall_score': 0,
            'scores': {},
            'issues': {
                'critical': [],
                'high': [],
                'medium': [],
                'low': [],
            },
            'recommendations': [],
            'opportunities': [],
            'summary': {},
        }

        async with aiohttp.ClientSession() as session:
            try:
                # Fetch website
                async with session.get(url, headers=self.headers, timeout=15) as response:
                    if response.status != 200:
                        audit_result['error'] = f"Website returned status {response.status}"
                        return audit_result

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Run all audit modules
                    audit_result['seo'] = await self._audit_seo(soup, url)
                    audit_result['performance'] = await self._audit_performance(url, html)
                    audit_result['mobile'] = await self._audit_mobile_friendliness(soup)
                    audit_result['content'] = await self._audit_content(soup)
                    audit_result['technical'] = await self._audit_technical(soup, url)
                    audit_result['security'] = await self._audit_security(url)
                    audit_result['social_media'] = await self._audit_social_media(soup)
                    audit_result['marketing'] = await self._audit_marketing(soup)

                    # Calculate scores
                    audit_result = self._calculate_scores(audit_result)

                    # Generate recommendations
                    audit_result = self._generate_recommendations(audit_result)

                    # Identify opportunities for pitch
                    audit_result['opportunities'] = self._identify_opportunities(audit_result)

            except Exception as e:
                audit_result['error'] = str(e)

        return audit_result

    async def _audit_seo(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """SEO audit"""
        seo_data = {
            'score': 0,
            'issues': [],
            'good_practices': [],
        }

        # Title tag
        title = soup.find('title')
        if not title:
            seo_data['issues'].append({
                'severity': 'critical',
                'issue': 'Missing title tag',
                'recommendation': 'Add a descriptive title tag (50-60 characters)',
            })
        elif len(title.get_text()) > 60:
            seo_data['issues'].append({
                'severity': 'medium',
                'issue': 'Title tag too long',
                'recommendation': f'Reduce title from {len(title.get_text())} to 50-60 characters',
            })
        else:
            seo_data['good_practices'].append('Title tag present and optimized')

        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            seo_data['issues'].append({
                'severity': 'high',
                'issue': 'Missing meta description',
                'recommendation': 'Add meta description (150-160 characters) to improve click-through rates',
            })
        else:
            desc_length = len(meta_desc.get('content', ''))
            if desc_length > 160:
                seo_data['issues'].append({
                    'severity': 'medium',
                    'issue': 'Meta description too long',
                    'recommendation': f'Reduce from {desc_length} to 150-160 characters',
                })

        # H1 tags
        h1_tags = soup.find_all('h1')
        if len(h1_tags) == 0:
            seo_data['issues'].append({
                'severity': 'high',
                'issue': 'No H1 tag found',
                'recommendation': 'Add a single H1 tag with your main keyword',
            })
        elif len(h1_tags) > 1:
            seo_data['issues'].append({
                'severity': 'medium',
                'issue': f'{len(h1_tags)} H1 tags found',
                'recommendation': 'Use only one H1 tag per page',
            })

        # Images without alt text
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            seo_data['issues'].append({
                'severity': 'medium',
                'issue': f'{len(images_without_alt)} images missing alt text',
                'recommendation': 'Add descriptive alt text to all images for SEO and accessibility',
            })

        # Open Graph tags
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        if len(og_tags) < 4:
            seo_data['issues'].append({
                'severity': 'low',
                'issue': 'Incomplete Open Graph tags',
                'recommendation': 'Add og:title, og:description, og:image, og:url for better social sharing',
            })

        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if not canonical:
            seo_data['issues'].append({
                'severity': 'medium',
                'issue': 'Missing canonical URL',
                'recommendation': 'Add canonical URL to avoid duplicate content issues',
            })

        return seo_data

    async def _audit_performance(self, url: str, html: str) -> Dict[str, Any]:
        """Performance audit"""
        perf_data = {
            'score': 0,
            'issues': [],
            'metrics': {},
        }

        # Page size
        page_size_kb = len(html.encode('utf-8')) / 1024
        perf_data['metrics']['page_size_kb'] = round(page_size_kb, 2)

        if page_size_kb > 1000:
            perf_data['issues'].append({
                'severity': 'high',
                'issue': f'Large page size: {round(page_size_kb, 0)} KB',
                'recommendation': 'Optimize images, minify CSS/JS to reduce page size below 1MB',
            })

        # External scripts
        soup = BeautifulSoup(html, 'html.parser')
        external_scripts = [script for script in soup.find_all('script') if script.get('src')]
        perf_data['metrics']['external_scripts'] = len(external_scripts)

        if len(external_scripts) > 10:
            perf_data['issues'].append({
                'severity': 'medium',
                'issue': f'{len(external_scripts)} external scripts',
                'recommendation': 'Reduce number of external scripts, combine and minify where possible',
            })

        # CSS files
        css_files = soup.find_all('link', rel='stylesheet')
        perf_data['metrics']['css_files'] = len(css_files)

        if len(css_files) > 5:
            perf_data['issues'].append({
                'severity': 'medium',
                'issue': f'{len(css_files)} CSS files',
                'recommendation': 'Combine CSS files to reduce HTTP requests',
            })

        return perf_data

    async def _audit_mobile_friendliness(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Mobile responsiveness audit"""
        mobile_data = {
            'score': 0,
            'issues': [],
        }

        # Viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            mobile_data['issues'].append({
                'severity': 'critical',
                'issue': 'Missing viewport meta tag',
                'recommendation': 'Add <meta name="viewport" content="width=device-width, initial-scale=1"> for mobile optimization',
            })

        # Check for responsive framework indicators
        html_text = str(soup).lower()
        has_bootstrap = 'bootstrap' in html_text
        has_tailwind = 'tailwind' in html_text
        has_responsive_framework = has_bootstrap or has_tailwind

        if not has_responsive_framework:
            mobile_data['issues'].append({
                'severity': 'high',
                'issue': 'No responsive framework detected',
                'recommendation': 'Implement responsive design using Bootstrap, Tailwind, or custom media queries',
            })

        return mobile_data

    async def _audit_content(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Content quality audit"""
        content_data = {
            'score': 0,
            'issues': [],
            'metrics': {},
        }

        # Word count
        text = soup.get_text()
        words = text.split()
        word_count = len(words)
        content_data['metrics']['word_count'] = word_count

        if word_count < 300:
            content_data['issues'].append({
                'severity': 'high',
                'issue': f'Low content volume: {word_count} words',
                'recommendation': 'Add more quality content (aim for 500+ words) to improve SEO',
            })

        # Headings structure
        headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
        content_data['metrics']['headings'] = headings

        if sum(headings.values()) < 3:
            content_data['issues'].append({
                'severity': 'medium',
                'issue': 'Poor heading structure',
                'recommendation': 'Use H2, H3 tags to organize content hierarchically',
            })

        # Links
        internal_links = len([a for a in soup.find_all('a') if a.get('href', '').startswith('/')])
        external_links = len([a for a in soup.find_all('a') if a.get('href', '').startswith('http')])
        content_data['metrics']['internal_links'] = internal_links
        content_data['metrics']['external_links'] = external_links

        return content_data

    async def _audit_technical(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Technical SEO audit"""
        tech_data = {
            'score': 0,
            'issues': [],
        }

        # Robots meta tag
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots and 'noindex' in robots.get('content', '').lower():
            tech_data['issues'].append({
                'severity': 'critical',
                'issue': 'Page set to noindex',
                'recommendation': 'Remove noindex if you want this page to appear in search results',
            })

        # Structured data
        json_ld = soup.find_all('script', type='application/ld+json')
        if not json_ld:
            tech_data['issues'].append({
                'severity': 'medium',
                'issue': 'No structured data (Schema.org) found',
                'recommendation': 'Add JSON-LD structured data for better search visibility (LocalBusiness, Organization, etc.)',
            })

        # HTTPS
        if not url.startswith('https://'):
            tech_data['issues'].append({
                'severity': 'critical',
                'issue': 'Website not using HTTPS',
                'recommendation': 'Install SSL certificate immediately for security and SEO',
            })

        return tech_data

    async def _audit_security(self, url: str) -> Dict[str, Any]:
        """Security audit"""
        security_data = {
            'score': 0,
            'issues': [],
        }

        # HTTPS check
        if not url.startswith('https://'):
            security_data['issues'].append({
                'severity': 'critical',
                'issue': 'No SSL/HTTPS encryption',
                'recommendation': 'Install SSL certificate from Let\'s Encrypt (free) or paid provider',
                'impact': 'Critical for user trust and Google rankings',
            })

        return security_data

    async def _audit_social_media(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Social media presence audit"""
        social_data = {
            'score': 0,
            'issues': [],
            'found_profiles': [],
        }

        # Look for social media links
        social_platforms = {
            'facebook': ['facebook.com', 'fb.com'],
            'twitter': ['twitter.com', 'x.com'],
            'instagram': ['instagram.com'],
            'linkedin': ['linkedin.com'],
            'youtube': ['youtube.com'],
        }

        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '').lower()
            for platform, domains in social_platforms.items():
                if any(domain in href for domain in domains):
                    social_data['found_profiles'].append({
                        'platform': platform,
                        'url': link.get('href'),
                    })

        missing_platforms = [p for p in social_platforms.keys() if p not in [sp['platform'] for sp in social_data['found_profiles']]]

        if missing_platforms:
            social_data['issues'].append({
                'severity': 'low',
                'issue': f'Missing social media profiles: {", ".join(missing_platforms)}',
                'recommendation': 'Create profiles on major platforms to expand reach',
            })

        return social_data

    async def _audit_marketing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Marketing elements audit"""
        marketing_data = {
            'score': 0,
            'issues': [],
            'found_elements': [],
        }

        # Call-to-action buttons
        cta_keywords = ['contact', 'call', 'book', 'schedule', 'get started', 'sign up', 'buy now']
        ctas = []
        for keyword in cta_keywords:
            buttons = soup.find_all(['button', 'a'], text=re.compile(keyword, re.I))
            ctas.extend(buttons)

        if len(ctas) < 2:
            marketing_data['issues'].append({
                'severity': 'high',
                'issue': 'Weak call-to-action',
                'recommendation': 'Add clear CTAs (Contact Us, Book Appointment, Get Quote) to increase conversions',
            })

        # Contact information
        has_phone = bool(re.search(r'\+?91[\s-]?[6-9]\d{9}', soup.get_text()))
        has_email = bool(soup.find('a', href=re.compile(r'^mailto:')))

        if not has_phone:
            marketing_data['issues'].append({
                'severity': 'high',
                'issue': 'No phone number found',
                'recommendation': 'Display phone number prominently for easy customer contact',
            })

        if not has_email:
            marketing_data['issues'].append({
                'severity': 'medium',
                'issue': 'No email contact found',
                'recommendation': 'Add visible email contact or contact form',
            })

        # Lead capture form
        forms = soup.find_all('form')
        has_lead_form = any('email' in str(form).lower() or 'name' in str(form).lower() for form in forms)

        if not has_lead_form:
            marketing_data['issues'].append({
                'severity': 'high',
                'issue': 'No lead capture form',
                'recommendation': 'Add email capture form to build your mailing list',
            })

        # Google Analytics
        has_analytics = 'google-analytics' in str(soup).lower() or 'gtag' in str(soup).lower()
        if not has_analytics:
            marketing_data['issues'].append({
                'severity': 'medium',
                'issue': 'No analytics tracking detected',
                'recommendation': 'Install Google Analytics to track website performance',
            })

        return marketing_data

    def _calculate_scores(self, audit_result: Dict) -> Dict:
        """Calculate scores for each category"""
        categories = ['seo', 'performance', 'mobile', 'content', 'technical', 'security', 'social_media', 'marketing']

        for category in categories:
            if category in audit_result and isinstance(audit_result[category], dict):
                issues = audit_result[category].get('issues', [])

                # Start with 100 and deduct points
                score = 100

                for issue in issues:
                    severity = issue.get('severity', 'low')
                    deduction = {
                        'critical': 25,
                        'high': 15,
                        'medium': 10,
                        'low': 5,
                    }.get(severity, 5)

                    score -= deduction

                    # Add to overall issues
                    audit_result['issues'][severity].append({
                        'category': category,
                        **issue
                    })

                audit_result['scores'][category] = max(0, score)

        # Overall score (weighted average)
        weights = {
            'seo': 0.25,
            'performance': 0.20,
            'mobile': 0.15,
            'content': 0.15,
            'technical': 0.10,
            'security': 0.10,
            'marketing': 0.05,
        }

        overall = sum(audit_result['scores'].get(cat, 0) * weight for cat, weight in weights.items())
        audit_result['overall_score'] = round(overall, 1)

        return audit_result

    def _generate_recommendations(self, audit_result: Dict) -> Dict:
        """Generate prioritized recommendations"""
        all_issues = []

        for severity in ['critical', 'high', 'medium', 'low']:
            all_issues.extend(audit_result['issues'][severity])

        # Sort by severity and create action plan
        priority_order = {'critical': 1, 'high': 2, 'medium': 3, 'low': 4}
        all_issues.sort(key=lambda x: priority_order.get(x.get('severity'), 5))

        audit_result['recommendations'] = all_issues[:10]  # Top 10 recommendations

        return audit_result

    def _identify_opportunities(self, audit_result: Dict) -> List[Dict]:
        """
        Identify specific opportunities for your digital marketing pitch
        These are STRONG pain points you can address
        """
        opportunities = []

        overall_score = audit_result.get('overall_score', 0)

        # Low overall score = big opportunity
        if overall_score < 60:
            opportunities.append({
                'type': 'website_redesign',
                'title': 'Website Redesign & Optimization',
                'description': f'Website score is only {overall_score}/100. A professional redesign could significantly improve online presence',
                'potential_impact': 'High',
                'pitch_angle': 'Your website needs urgent attention to compete effectively online',
            })

        # Missing SEO
        if audit_result.get('scores', {}).get('seo', 0) < 70:
            opportunities.append({
                'type': 'seo_services',
                'title': 'SEO Optimization',
                'description': 'Poor SEO is limiting your online visibility',
                'potential_impact': 'High',
                'pitch_angle': 'We can help you rank higher on Google and get more organic traffic',
            })

        # No mobile optimization
        if audit_result.get('scores', {}).get('mobile', 0) < 70:
            opportunities.append({
                'type': 'mobile_optimization',
                'title': 'Mobile Optimization',
                'description': 'Website is not mobile-friendly (60%+ of traffic is mobile)',
                'potential_impact': 'Critical',
                'pitch_angle': 'You\'re losing mobile customers due to poor mobile experience',
            })

        # Weak marketing
        if audit_result.get('scores', {}).get('marketing', 0) < 70:
            opportunities.append({
                'type': 'digital_marketing',
                'title': 'Digital Marketing Campaign',
                'description': 'Missing key marketing elements (CTAs, lead capture, analytics)',
                'potential_impact': 'High',
                'pitch_angle': 'Your website isn\'t converting visitors into leads effectively',
            })

        # No social presence
        social_profiles = audit_result.get('social_media', {}).get('found_profiles', [])
        if len(social_profiles) < 2:
            opportunities.append({
                'type': 'social_media_marketing',
                'title': 'Social Media Marketing',
                'description': 'Limited or no social media presence',
                'potential_impact': 'Medium',
                'pitch_angle': 'Expand your reach with professional social media management',
            })

        # No security (no HTTPS)
        if not audit_result.get('url', '').startswith('https://'):
            opportunities.append({
                'type': 'security_upgrade',
                'title': 'Security & Trust',
                'description': 'Website lacks SSL certificate (not secure)',
                'potential_impact': 'Critical',
                'pitch_angle': 'Your website shows "Not Secure" warning, damaging customer trust',
            })

        return opportunities


class LeadMagnetGenerator:
    """
    Generate professional lead magnets (audit reports) for outreach
    """

    def generate_pdf_report(self, audit_data: Dict) -> Dict:
        """
        Generate PDF audit report
        This is your lead magnet for outreach
        """
        # In production, use library like ReportLab or WeasyPrint
        # For now, return structured data for PDF generation

        report = {
            'title': f'Website Audit Report - {audit_data.get("url", "")}',
            'generated_at': datetime.utcnow().isoformat(),
            'sections': [],
        }

        # Executive Summary
        report['sections'].append({
            'title': 'Executive Summary',
            'content': self._generate_executive_summary(audit_data),
        })

        # Scorecard
        report['sections'].append({
            'title': 'Performance Scorecard',
            'content': audit_data.get('scores', {}),
        })

        # Critical Issues
        critical_issues = audit_data.get('issues', {}).get('critical', [])
        if critical_issues:
            report['sections'].append({
                'title': 'Critical Issues (Immediate Action Required)',
                'content': critical_issues,
            })

        # Opportunities
        report['sections'].append({
            'title': 'Growth Opportunities',
            'content': audit_data.get('opportunities', []),
        })

        # Recommendations
        report['sections'].append({
            'title': 'Recommended Action Plan',
            'content': audit_data.get('recommendations', [])[:10],
        })

        return report

    def _generate_executive_summary(self, audit_data: Dict) -> str:
        """Generate executive summary text"""
        score = audit_data.get('overall_score', 0)

        if score >= 80:
            summary = f"Your website scored {score}/100, which is excellent. However, there are still opportunities to optimize further."
        elif score >= 60:
            summary = f"Your website scored {score}/100. While functional, there are significant opportunities for improvement that could increase your online performance."
        else:
            summary = f"Your website scored {score}/100, indicating critical issues that need immediate attention. Your online presence is significantly underperforming."

        critical_count = len(audit_data.get('issues', {}).get('critical', []))
        high_count = len(audit_data.get('issues', {}).get('high', []))

        if critical_count > 0:
            summary += f" We found {critical_count} critical issues and {high_count} high-priority issues that are limiting your online success."

        return summary

    def generate_email_template(self, company_name: str, audit_data: Dict, decision_maker: Optional[str] = None) -> str:
        """
        Generate personalized outreach email with audit insights
        """
        name = decision_maker or "there"
        score = audit_data.get('overall_score', 0)
        top_issues = audit_data.get('issues', {}).get('critical', []) + audit_data.get('issues', {}).get('high', [])

        email = f"""
Subject: Free Website Audit for {company_name} - Score: {score}/100

Hi {name},

I recently came across {company_name}'s website and ran a comprehensive digital audit. I wanted to share some findings that could significantly impact your online performance.

Your website currently scores {score}/100. Here are the most critical issues I found:

"""

        for i, issue in enumerate(top_issues[:3], 1):
            email += f"{i}. {issue.get('issue', '')} - {issue.get('recommendation', '')}\n"

        email += f"""

I've prepared a detailed audit report (attached) showing exactly how to improve your online presence and attract more customers.

Would you be interested in a quick 15-minute call to discuss how we can help improve these metrics?

Best regards,
[Your Name]
[Your Agency]
[Contact]

P.S. Based on my analysis, implementing just the top 3 recommendations could increase your website traffic by 30-50%.
"""

        return email
