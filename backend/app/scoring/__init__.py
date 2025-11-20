"""
AI Lead Scoring System
Machine learning-based lead scoring and prioritization
"""

from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LeadScorer:
    """
    AI-powered lead scoring using machine learning

    Features:
    - Multi-factor scoring algorithm
    - Customizable weights
    - Historical performance learning
    - Fit score and intent score calculation
    """

    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.feature_weights = {
            # Company attributes
            'employee_count': 15,
            'revenue': 15,
            'founded_year': 5,

            # Contact information quality
            'has_email': 10,
            'email_verified': 10,
            'has_phone': 8,
            'phone_verified': 7,
            'has_decision_maker': 12,

            # Engagement signals
            'is_hiring': 10,
            'job_openings_count': 8,
            'recent_funding': 10,
            'funding_amount': 8,

            # Technology fit
            'tech_stack_match': 12,
            'cms_platform': 5,
            'ecommerce_platform': 5,

            # Online presence
            'has_website': 8,
            'linkedin_followers': 5,
            'social_media_presence': 5,

            # Data quality
            'data_completeness': 10,
            'is_enriched': 8,
        }

    def calculate_lead_score(self, lead_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate comprehensive lead score

        Args:
            lead_data: Lead information dictionary

        Returns:
            Dictionary with lead_score, fit_score, intent_score, and factors
        """
        fit_score = self._calculate_fit_score(lead_data)
        intent_score = self._calculate_intent_score(lead_data)

        # Overall lead score (weighted average)
        lead_score = (fit_score * 0.5) + (intent_score * 0.5)

        # Get scoring factors breakdown
        factors = self._get_scoring_factors(lead_data)

        return {
            'lead_score': round(lead_score, 2),
            'fit_score': round(fit_score, 2),
            'intent_score': round(intent_score, 2),
            'factors': factors,
            'scored_at': datetime.utcnow().isoformat()
        }

    def _calculate_fit_score(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate how well the lead fits the ideal customer profile

        Args:
            lead_data: Lead information

        Returns:
            Fit score (0-100)
        """
        score = 0.0
        max_score = 0.0

        # Company size scoring
        employee_count = lead_data.get('employee_count', 0)
        if employee_count:
            max_score += self.feature_weights['employee_count']
            if 10 <= employee_count <= 1000:  # Ideal range
                score += self.feature_weights['employee_count']
            elif 1 <= employee_count <= 10 or 1000 < employee_count <= 5000:
                score += self.feature_weights['employee_count'] * 0.7
            else:
                score += self.feature_weights['employee_count'] * 0.3

        # Revenue scoring
        revenue = lead_data.get('annual_revenue', 0)
        if revenue:
            max_score += self.feature_weights['revenue']
            if 1_000_000 <= revenue <= 50_000_000:  # Ideal range
                score += self.feature_weights['revenue']
            elif 100_000 <= revenue < 1_000_000 or 50_000_000 < revenue <= 100_000_000:
                score += self.feature_weights['revenue'] * 0.7
            else:
                score += self.feature_weights['revenue'] * 0.3

        # Company age
        founded_year = lead_data.get('founded_year')
        if founded_year:
            max_score += self.feature_weights['founded_year']
            age = datetime.now().year - founded_year
            if 2 <= age <= 10:  # Sweet spot
                score += self.feature_weights['founded_year']
            elif age > 10:
                score += self.feature_weights['founded_year'] * 0.7
            else:
                score += self.feature_weights['founded_year'] * 0.5

        # Contact information
        max_score += self.feature_weights['has_email']
        if lead_data.get('email') or lead_data.get('contact_email'):
            score += self.feature_weights['has_email']

        max_score += self.feature_weights['email_verified']
        if lead_data.get('email_verified'):
            score += self.feature_weights['email_verified']

        max_score += self.feature_weights['has_phone']
        if lead_data.get('phone') or lead_data.get('contact_phone'):
            score += self.feature_weights['has_phone']

        max_score += self.feature_weights['phone_verified']
        if lead_data.get('phone_verified'):
            score += self.feature_weights['phone_verified']

        max_score += self.feature_weights['has_decision_maker']
        if lead_data.get('contact_name') and lead_data.get('contact_title'):
            score += self.feature_weights['has_decision_maker']

        # Technology fit
        max_score += self.feature_weights['tech_stack_match']
        technologies = lead_data.get('technologies', [])
        if technologies:
            # Score based on how many desired technologies they use
            desired_techs = ['React', 'Python', 'Node.js', 'AWS', 'Salesforce', 'HubSpot']
            matches = sum(1 for tech in technologies if tech in desired_techs)
            tech_score = (matches / len(desired_techs)) * self.feature_weights['tech_stack_match']
            score += tech_score

        # Online presence
        max_score += self.feature_weights['has_website']
        if lead_data.get('company_website'):
            score += self.feature_weights['has_website']

        max_score += self.feature_weights['linkedin_followers']
        linkedin_followers = lead_data.get('linkedin_followers', 0)
        if linkedin_followers:
            if linkedin_followers >= 10000:
                score += self.feature_weights['linkedin_followers']
            elif linkedin_followers >= 1000:
                score += self.feature_weights['linkedin_followers'] * 0.7
            else:
                score += self.feature_weights['linkedin_followers'] * 0.3

        # Data quality
        max_score += self.feature_weights['data_completeness']
        completeness = self._calculate_data_completeness(lead_data)
        score += completeness * self.feature_weights['data_completeness']

        max_score += self.feature_weights['is_enriched']
        if lead_data.get('is_enriched'):
            score += self.feature_weights['is_enriched']

        # Normalize to 0-100 scale
        if max_score > 0:
            return (score / max_score) * 100
        return 0.0

    def _calculate_intent_score(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate buying intent based on growth signals

        Args:
            lead_data: Lead information

        Returns:
            Intent score (0-100)
        """
        score = 0.0
        max_score = 0.0

        # Hiring signals
        max_score += self.feature_weights['is_hiring']
        if lead_data.get('is_hiring'):
            score += self.feature_weights['is_hiring']

        max_score += self.feature_weights['job_openings_count']
        job_openings = lead_data.get('job_openings_count', 0)
        if job_openings > 0:
            opening_score = min(job_openings / 20, 1.0)  # Cap at 20 openings
            score += opening_score * self.feature_weights['job_openings_count']

        # Funding signals
        max_score += self.feature_weights['recent_funding']
        if lead_data.get('recent_funding'):
            score += self.feature_weights['recent_funding']

        max_score += self.feature_weights['funding_amount']
        funding = lead_data.get('funding_amount', 0)
        if funding > 0:
            if funding >= 10_000_000:
                score += self.feature_weights['funding_amount']
            elif funding >= 1_000_000:
                score += self.feature_weights['funding_amount'] * 0.7
            else:
                score += self.feature_weights['funding_amount'] * 0.4

        # Recent news/activity
        recent_news = lead_data.get('recent_news', [])
        if recent_news:
            score += 10  # Bonus for being in the news
            max_score += 10

        # Normalize to 0-100 scale
        if max_score > 0:
            return (score / max_score) * 100
        return 0.0

    def _calculate_data_completeness(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate how complete the lead data is

        Args:
            lead_data: Lead information

        Returns:
            Completeness score (0-1)
        """
        important_fields = [
            'company_name', 'company_website', 'email', 'phone',
            'industry', 'employee_count', 'city', 'state', 'country',
            'company_description', 'linkedin_url'
        ]

        filled_fields = sum(1 for field in important_fields if lead_data.get(field))
        return filled_fields / len(important_fields)

    def _get_scoring_factors(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed breakdown of scoring factors

        Args:
            lead_data: Lead information

        Returns:
            Dictionary of scoring factors
        """
        return {
            'company_size': {
                'employees': lead_data.get('employee_count'),
                'revenue': lead_data.get('annual_revenue'),
            },
            'contact_quality': {
                'has_email': bool(lead_data.get('email') or lead_data.get('contact_email')),
                'email_verified': lead_data.get('email_verified', False),
                'has_phone': bool(lead_data.get('phone') or lead_data.get('contact_phone')),
                'has_decision_maker': bool(lead_data.get('contact_name')),
            },
            'growth_signals': {
                'is_hiring': lead_data.get('is_hiring', False),
                'job_openings': lead_data.get('job_openings_count', 0),
                'recent_funding': lead_data.get('recent_funding', False),
                'funding_amount': lead_data.get('funding_amount'),
            },
            'technology': {
                'tech_count': len(lead_data.get('technologies', [])),
                'technologies': lead_data.get('technologies', []),
            },
            'data_quality': {
                'completeness': self._calculate_data_completeness(lead_data),
                'is_enriched': lead_data.get('is_enriched', False),
            }
        }

    def batch_score_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score multiple leads efficiently

        Args:
            leads: List of lead data dictionaries

        Returns:
            List of scoring results
        """
        results = []
        for lead in leads:
            try:
                score_result = self.calculate_lead_score(lead)
                results.append({
                    'lead_id': lead.get('id'),
                    'company_name': lead.get('company_name'),
                    **score_result
                })
            except Exception as e:
                logger.error(f"Error scoring lead {lead.get('id')}: {str(e)}")
                results.append({
                    'lead_id': lead.get('id'),
                    'error': str(e)
                })

        return results

    def train_model(self, historical_data: List[Dict[str, Any]], labels: List[int]):
        """
        Train ML model on historical conversion data

        Args:
            historical_data: List of lead features
            labels: Conversion outcomes (1 = converted, 0 = not converted)
        """
        logger.info(f"Training model on {len(historical_data)} historical leads")

        # Extract features
        X = self._extract_features(historical_data)
        y = np.array(labels)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train model
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.model.fit(X_scaled, y)

        logger.info("Model training completed")

    def _extract_features(self, leads: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract numerical features from lead data for ML

        Args:
            leads: List of lead data

        Returns:
            Feature matrix
        """
        features = []

        for lead in leads:
            lead_features = [
                lead.get('employee_count', 0),
                lead.get('annual_revenue', 0),
                1 if lead.get('email') else 0,
                1 if lead.get('email_verified') else 0,
                1 if lead.get('phone') else 0,
                1 if lead.get('is_hiring') else 0,
                lead.get('job_openings_count', 0),
                1 if lead.get('recent_funding') else 0,
                lead.get('funding_amount', 0),
                len(lead.get('technologies', [])),
                self._calculate_data_completeness(lead),
            ]
            features.append(lead_features)

        return np.array(features)

    def predict_conversion_probability(self, lead_data: Dict[str, Any]) -> float:
        """
        Predict probability of lead conversion using ML model

        Args:
            lead_data: Lead information

        Returns:
            Conversion probability (0-1)
        """
        if self.model is None:
            logger.warning("Model not trained, using rule-based scoring")
            score = self.calculate_lead_score(lead_data)
            return score['lead_score'] / 100

        # Extract and scale features
        features = self._extract_features([lead_data])
        features_scaled = self.scaler.transform(features)

        # Predict probability
        probability = self.model.predict_proba(features_scaled)[0][1]

        return probability

    def save_model(self, path: str):
        """Save trained model to disk"""
        if self.model:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler,
                'feature_weights': self.feature_weights
            }, path)
            logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load trained model from disk"""
        try:
            data = joblib.load(path)
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_weights = data['feature_weights']
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")


class CustomScoringEngine:
    """
    Custom scoring engine for user-defined criteria

    Allows users to create custom scoring rules
    """

    def __init__(self, scoring_rules: Dict[str, Any]):
        """
        Initialize custom scoring engine

        Args:
            scoring_rules: Dictionary of custom scoring rules
        """
        self.rules = scoring_rules

    def calculate_score(self, lead_data: Dict[str, Any]) -> float:
        """
        Calculate score based on custom rules

        Args:
            lead_data: Lead information

        Returns:
            Custom score (0-100)
        """
        score = 0.0
        max_score = 0.0

        for rule_name, rule_config in self.rules.items():
            field = rule_config['field']
            weight = rule_config['weight']
            condition = rule_config['condition']

            max_score += weight

            if self._evaluate_condition(lead_data.get(field), condition):
                score += weight

        if max_score > 0:
            return (score / max_score) * 100
        return 0.0

    def _evaluate_condition(self, value: Any, condition: Dict[str, Any]) -> bool:
        """
        Evaluate a condition

        Args:
            value: Field value
            condition: Condition to evaluate

        Returns:
            True if condition is met
        """
        operator = condition.get('operator')
        target = condition.get('value')

        if operator == 'equals':
            return value == target
        elif operator == 'greater_than':
            return value > target if value else False
        elif operator == 'less_than':
            return value < target if value else False
        elif operator == 'contains':
            return target in value if value else False
        elif operator == 'exists':
            return bool(value)

        return False
