"""
Scraper Testing Framework
Comprehensive testing and quality assurance for scrapers
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import time
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ScraperTest:
    """
    Individual scraper test case

    Tests can validate:
    - Data extraction accuracy
    - Performance metrics
    - Error handling
    - Anti-detection effectiveness
    """

    def __init__(
        self,
        name: str,
        description: str,
        test_function: Callable,
        expected_result: Optional[Any] = None,
        timeout: int = 60,
    ):
        self.name = name
        self.description = description
        self.test_function = test_function
        self.expected_result = expected_result
        self.timeout = timeout

        self.status = "pending"  # pending, running, passed, failed
        self.result = None
        self.error = None
        self.duration = 0.0
        self.executed_at: Optional[datetime] = None

    async def run(self) -> Dict[str, Any]:
        """
        Run the test

        Returns:
            Test result dictionary
        """
        self.status = "running"
        self.executed_at = datetime.utcnow()

        start_time = time.time()

        try:
            # Run test with timeout
            self.result = await asyncio.wait_for(
                self.test_function(),
                timeout=self.timeout
            )

            # Validate result
            if self.expected_result is not None:
                if self.result == self.expected_result:
                    self.status = "passed"
                else:
                    self.status = "failed"
                    self.error = f"Expected {self.expected_result}, got {self.result}"
            else:
                # No expected result, just check if it ran without error
                self.status = "passed"

        except asyncio.TimeoutError:
            self.status = "failed"
            self.error = f"Test timed out after {self.timeout} seconds"

        except Exception as e:
            self.status = "failed"
            self.error = str(e)

        finally:
            self.duration = time.time() - start_time

        return self.to_dict()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'duration': round(self.duration, 2),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
        }


class ScraperTestSuite:
    """
    Collection of scraper tests

    Organizes and runs multiple tests for comprehensive validation
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tests: List[ScraperTest] = []

    def add_test(self, test: ScraperTest):
        """Add test to suite"""
        self.tests.append(test)

    async def run_all(self) -> Dict[str, Any]:
        """
        Run all tests in the suite

        Returns:
            Suite results
        """
        logger.info(f"Running test suite: {self.name}")

        start_time = time.time()

        # Run tests concurrently
        tasks = [test.run() for test in self.tests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        duration = time.time() - start_time

        # Calculate statistics
        passed = sum(1 for t in self.tests if t.status == "passed")
        failed = sum(1 for t in self.tests if t.status == "failed")

        return {
            'suite_name': self.name,
            'description': self.description,
            'total_tests': len(self.tests),
            'passed': passed,
            'failed': failed,
            'success_rate': round((passed / len(self.tests) * 100) if self.tests else 0, 2),
            'duration': round(duration, 2),
            'tests': [t.to_dict() for t in self.tests],
        }


class QualityValidator:
    """
    Validates scraped data quality

    Checks for:
    - Data completeness
    - Format correctness
    - Duplicate detection
    - Anomaly detection
    """

    def __init__(self):
        self.validation_rules = []

    def validate_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate single lead data

        Args:
            lead_data: Lead data dictionary

        Returns:
            Validation result
        """
        issues = []
        warnings = []
        score = 100

        # Check required fields
        required_fields = ['company_name']
        for field in required_fields:
            if not lead_data.get(field):
                issues.append(f"Missing required field: {field}")
                score -= 30

        # Check email format
        email = lead_data.get('email')
        if email and not self._is_valid_email(email):
            issues.append(f"Invalid email format: {email}")
            score -= 15

        # Check phone format
        phone = lead_data.get('phone')
        if phone and not self._is_valid_phone(phone):
            warnings.append(f"Suspicious phone format: {phone}")
            score -= 5

        # Check for suspicious patterns
        company_name = lead_data.get('company_name', '')
        suspicious_words = ['test', 'example', 'sample', 'demo', 'lorem', 'ipsum']
        if any(word in company_name.lower() for word in suspicious_words):
            issues.append(f"Suspicious company name: {company_name}")
            score -= 20

        # Check data completeness
        important_fields = ['company_website', 'email', 'phone', 'industry', 'city']
        filled = sum(1 for field in important_fields if lead_data.get(field))
        completeness = (filled / len(important_fields)) * 100

        if completeness < 40:
            warnings.append(f"Low data completeness: {completeness:.0f}%")
            score -= 10

        # Ensure score doesn't go negative
        score = max(score, 0)

        return {
            'valid': len(issues) == 0,
            'score': score,
            'completeness': round(completeness, 2),
            'issues': issues,
            'warnings': warnings,
        }

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def _is_valid_phone(self, phone: str) -> bool:
        """Validate phone format"""
        import re
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        # Check if it's mostly digits
        return len(cleaned) >= 10 and cleaned.replace('+', '').replace('1', '', 1).isdigit()

    def batch_validate(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate multiple leads

        Args:
            leads: List of lead data

        Returns:
            Batch validation results
        """
        results = [self.validate_lead(lead) for lead in leads]

        valid_count = sum(1 for r in results if r['valid'])
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        avg_completeness = sum(r['completeness'] for r in results) / len(results) if results else 0

        # Find common issues
        all_issues = []
        for r in results:
            all_issues.extend(r['issues'])

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        return {
            'total_leads': len(leads),
            'valid_leads': valid_count,
            'invalid_leads': len(leads) - valid_count,
            'validation_rate': round((valid_count / len(leads) * 100) if leads else 0, 2),
            'avg_quality_score': round(avg_score, 2),
            'avg_completeness': round(avg_completeness, 2),
            'common_issues': dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'individual_results': results[:10],  # First 10 for preview
        }

    def detect_duplicates(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect duplicate leads

        Args:
            leads: List of lead data

        Returns:
            List of duplicate groups
        """
        duplicates = []
        seen = {}

        for idx, lead in enumerate(leads):
            # Create fingerprint
            fingerprint = self._create_fingerprint(lead)

            if fingerprint in seen:
                # Found duplicate
                duplicates.append({
                    'original_index': seen[fingerprint],
                    'duplicate_index': idx,
                    'fingerprint': fingerprint,
                    'original': leads[seen[fingerprint]],
                    'duplicate': lead,
                })
            else:
                seen[fingerprint] = idx

        return duplicates

    def _create_fingerprint(self, lead: Dict[str, Any]) -> str:
        """
        Create unique fingerprint for lead

        Args:
            lead: Lead data

        Returns:
            Fingerprint string
        """
        import hashlib

        # Use company name, website, and email as fingerprint
        parts = [
            str(lead.get('company_name', '')).lower().strip(),
            str(lead.get('company_website', '')).lower().strip(),
            str(lead.get('email', '')).lower().strip(),
        ]

        fingerprint_string = '|'.join(parts)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()


class ScraperBenchmark:
    """
    Benchmark scraper performance

    Measures:
    - Speed (leads per minute)
    - Accuracy (data quality)
    - Reliability (success rate)
    - Efficiency (resource usage)
    """

    def __init__(self):
        self.benchmarks = []

    async def run_benchmark(
        self,
        scraper_name: str,
        scraper_function: Callable,
        test_data: List[str],
    ) -> Dict[str, Any]:
        """
        Run performance benchmark

        Args:
            scraper_name: Name of scraper
            scraper_function: Scraper function to benchmark
            test_data: Test URLs or data

        Returns:
            Benchmark results
        """
        logger.info(f"Running benchmark for {scraper_name}")

        start_time = time.time()
        results = []
        errors = 0

        for item in test_data:
            try:
                result = await scraper_function(item)
                if result:
                    results.append(result)
            except Exception as e:
                errors += 1
                logger.error(f"Benchmark error: {str(e)}")

        duration = time.time() - start_time

        # Calculate metrics
        leads_per_minute = (len(results) / duration) * 60 if duration > 0 else 0
        success_rate = ((len(test_data) - errors) / len(test_data) * 100) if test_data else 0

        # Validate quality
        validator = QualityValidator()
        quality_results = validator.batch_validate(results)

        benchmark_result = {
            'scraper_name': scraper_name,
            'test_size': len(test_data),
            'duration': round(duration, 2),
            'leads_found': len(results),
            'errors': errors,
            'success_rate': round(success_rate, 2),
            'leads_per_minute': round(leads_per_minute, 2),
            'avg_quality_score': quality_results['avg_quality_score'],
            'avg_completeness': quality_results['avg_completeness'],
            'timestamp': datetime.utcnow().isoformat(),
        }

        self.benchmarks.append(benchmark_result)

        return benchmark_result

    def compare_scrapers(self, scraper_names: List[str]) -> Dict[str, Any]:
        """
        Compare multiple scrapers

        Args:
            scraper_names: List of scraper names to compare

        Returns:
            Comparison results
        """
        comparisons = []

        for name in scraper_names:
            scraper_benchmarks = [b for b in self.benchmarks if b['scraper_name'] == name]

            if scraper_benchmarks:
                avg_speed = sum(b['leads_per_minute'] for b in scraper_benchmarks) / len(scraper_benchmarks)
                avg_quality = sum(b['avg_quality_score'] for b in scraper_benchmarks) / len(scraper_benchmarks)
                avg_success = sum(b['success_rate'] for b in scraper_benchmarks) / len(scraper_benchmarks)

                comparisons.append({
                    'scraper_name': name,
                    'avg_speed': round(avg_speed, 2),
                    'avg_quality': round(avg_quality, 2),
                    'avg_success_rate': round(avg_success, 2),
                    'total_runs': len(scraper_benchmarks),
                })

        # Sort by overall score (weighted average)
        for comp in comparisons:
            comp['overall_score'] = round(
                (comp['avg_speed'] * 0.3) +
                (comp['avg_quality'] * 0.4) +
                (comp['avg_success_rate'] * 0.3),
                2
            )

        comparisons.sort(key=lambda x: x['overall_score'], reverse=True)

        return {
            'comparison': comparisons,
            'winner': comparisons[0]['scraper_name'] if comparisons else None,
        }


# Global instances
quality_validator = QualityValidator()
scraper_benchmark = ScraperBenchmark()
