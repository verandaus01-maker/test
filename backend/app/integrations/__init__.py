"""
CRM Integrations
Connect with HubSpot, Salesforce, Pipedrive, and other CRM systems
"""

from typing import Dict, Any, List, Optional
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseCRMIntegration:
    """Base class for CRM integrations"""

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize CRM integration

        Args:
            api_key: API key or access token
            **kwargs: Additional configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self):
        """Establish connection to CRM"""
        self.session = aiohttp.ClientSession()

    async def disconnect(self):
        """Close connection"""
        if self.session:
            await self.session.close()

    async def test_connection(self) -> bool:
        """Test if connection is valid"""
        raise NotImplementedError

    async def create_contact(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create contact in CRM"""
        raise NotImplementedError

    async def update_contact(self, contact_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing contact"""
        raise NotImplementedError

    async def find_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Find contact by email"""
        raise NotImplementedError

    async def sync_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync lead to CRM (create or update)"""
        email = lead_data.get('email') or lead_data.get('contact_email')

        if not email:
            raise ValueError("Email is required to sync lead")

        # Check if contact exists
        existing = await self.find_contact(email)

        if existing:
            return await self.update_contact(existing['id'], lead_data)
        else:
            return await self.create_contact(lead_data)


class HubSpotIntegration(BaseCRMIntegration):
    """
    HubSpot CRM Integration

    Supports:
    - Creating/updating contacts
    - Creating companies
    - Creating deals
    - Syncing lead data
    """

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = "https://api.hubapi.com"

    async def test_connection(self) -> bool:
        """Test HubSpot connection"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            url = f"{self.base_url}/crm/v3/objects/contacts"

            async with self.session.get(url, headers=headers, params={'limit': 1}) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"HubSpot connection test failed: {str(e)}")
            return False

    async def create_contact(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create contact in HubSpot

        Args:
            lead_data: Lead information

        Returns:
            Created contact data
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Map lead data to HubSpot properties
        properties = {
            "email": lead_data.get('email') or lead_data.get('contact_email'),
            "firstname": lead_data.get('contact_name', '').split()[0] if lead_data.get('contact_name') else '',
            "lastname": ' '.join(lead_data.get('contact_name', '').split()[1:]) if lead_data.get('contact_name') else '',
            "company": lead_data.get('company_name'),
            "website": lead_data.get('company_website'),
            "phone": lead_data.get('phone') or lead_data.get('contact_phone'),
            "jobtitle": lead_data.get('contact_title'),
            "city": lead_data.get('city'),
            "state": lead_data.get('state'),
            "country": lead_data.get('country'),
            "industry": lead_data.get('industry'),
            "hs_lead_status": "NEW",
        }

        # Remove None values
        properties = {k: v for k, v in properties.items() if v is not None}

        url = f"{self.base_url}/crm/v3/objects/contacts"
        payload = {"properties": properties}

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"HubSpot API error: {error_text}")
        except Exception as e:
            logger.error(f"Error creating HubSpot contact: {str(e)}")
            raise

    async def update_contact(self, contact_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update contact in HubSpot"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        properties = {
            "company": lead_data.get('company_name'),
            "website": lead_data.get('company_website'),
            "phone": lead_data.get('phone') or lead_data.get('contact_phone'),
            "jobtitle": lead_data.get('contact_title'),
            "city": lead_data.get('city'),
            "state": lead_data.get('state'),
            "industry": lead_data.get('industry'),
        }

        properties = {k: v for k, v in properties.items() if v is not None}

        url = f"{self.base_url}/crm/v3/objects/contacts/{contact_id}"
        payload = {"properties": properties}

        try:
            async with self.session.patch(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"HubSpot API error: {error_text}")
        except Exception as e:
            logger.error(f"Error updating HubSpot contact: {str(e)}")
            raise

    async def find_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Find contact by email in HubSpot"""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        url = f"{self.base_url}/crm/v3/objects/contacts/search"
        payload = {
            "filterGroups": [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email
                }]
            }]
        }

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', [])
                    return results[0] if results else None
                return None
        except Exception as e:
            logger.error(f"Error finding HubSpot contact: {str(e)}")
            return None

    async def create_company(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create company in HubSpot"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        properties = {
            "name": lead_data.get('company_name'),
            "domain": lead_data.get('company_domain'),
            "industry": lead_data.get('industry'),
            "city": lead_data.get('city'),
            "state": lead_data.get('state'),
            "country": lead_data.get('country'),
            "phone": lead_data.get('phone'),
            "numberofemployees": lead_data.get('employee_count'),
            "annualrevenue": lead_data.get('annual_revenue'),
            "description": lead_data.get('company_description'),
        }

        properties = {k: v for k, v in properties.items() if v is not None}

        url = f"{self.base_url}/crm/v3/objects/companies"
        payload = {"properties": properties}

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"HubSpot API error: {error_text}")
        except Exception as e:
            logger.error(f"Error creating HubSpot company: {str(e)}")
            raise


class SalesforceIntegration(BaseCRMIntegration):
    """
    Salesforce CRM Integration

    Supports:
    - Creating/updating leads
    - Converting leads to contacts
    - Creating opportunities
    """

    def __init__(self, username: str, password: str, security_token: str, **kwargs):
        super().__init__(api_key="", **kwargs)
        self.username = username
        self.password = password
        self.security_token = security_token
        self.instance_url = None
        self.access_token = None

    async def connect(self):
        """Connect to Salesforce and get access token"""
        await super().connect()

        # Authenticate
        auth_url = "https://login.salesforce.com/services/oauth2/token"

        data = {
            'grant_type': 'password',
            'client_id': self.config.get('client_id'),
            'client_secret': self.config.get('client_secret'),
            'username': self.username,
            'password': f"{self.password}{self.security_token}"
        }

        try:
            async with self.session.post(auth_url, data=data) as response:
                if response.status == 200:
                    auth_data = await response.json()
                    self.access_token = auth_data['access_token']
                    self.instance_url = auth_data['instance_url']
                    logger.info("Salesforce authentication successful")
                else:
                    raise Exception("Salesforce authentication failed")
        except Exception as e:
            logger.error(f"Salesforce connection error: {str(e)}")
            raise

    async def test_connection(self) -> bool:
        """Test Salesforce connection"""
        if not self.access_token:
            return False

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            url = f"{self.instance_url}/services/data/v57.0/sobjects/Lead/describe"

            async with self.session.get(url, headers=headers) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Salesforce connection test failed: {str(e)}")
            return False

    async def create_contact(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create lead in Salesforce"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        # Split name
        contact_name = lead_data.get('contact_name', '')
        name_parts = contact_name.split() if contact_name else ['', '']

        payload = {
            "FirstName": name_parts[0] if len(name_parts) > 0 else '',
            "LastName": name_parts[-1] if len(name_parts) > 1 else contact_name,
            "Email": lead_data.get('email') or lead_data.get('contact_email'),
            "Company": lead_data.get('company_name'),
            "Phone": lead_data.get('phone') or lead_data.get('contact_phone'),
            "Title": lead_data.get('contact_title'),
            "Website": lead_data.get('company_website'),
            "City": lead_data.get('city'),
            "State": lead_data.get('state'),
            "Country": lead_data.get('country'),
            "Industry": lead_data.get('industry'),
            "NumberOfEmployees": lead_data.get('employee_count'),
            "AnnualRevenue": lead_data.get('annual_revenue'),
            "Status": "Open - Not Contacted",
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None and v != ''}

        url = f"{self.instance_url}/services/data/v57.0/sobjects/Lead"

        try:
            async with self.session.post(url, headers=headers, json=payload) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"Salesforce API error: {error_text}")
        except Exception as e:
            logger.error(f"Error creating Salesforce lead: {str(e)}")
            raise

    async def update_contact(self, contact_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update lead in Salesforce"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "Company": lead_data.get('company_name'),
            "Phone": lead_data.get('phone') or lead_data.get('contact_phone'),
            "Title": lead_data.get('contact_title'),
            "City": lead_data.get('city'),
            "State": lead_data.get('state'),
            "Industry": lead_data.get('industry'),
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        url = f"{self.instance_url}/services/data/v57.0/sobjects/Lead/{contact_id}"

        try:
            async with self.session.patch(url, headers=headers, json=payload) as response:
                if response.status == 204:
                    return {"id": contact_id, "success": True}
                else:
                    error_text = await response.text()
                    raise Exception(f"Salesforce API error: {error_text}")
        except Exception as e:
            logger.error(f"Error updating Salesforce lead: {str(e)}")
            raise

    async def find_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Find lead by email in Salesforce"""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        # SOQL query
        query = f"SELECT Id, Email, FirstName, LastName FROM Lead WHERE Email = '{email}' LIMIT 1"
        url = f"{self.instance_url}/services/data/v57.0/query"

        try:
            async with self.session.get(url, headers=headers, params={'q': query}) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get('records', [])
                    return records[0] if records else None
                return None
        except Exception as e:
            logger.error(f"Error finding Salesforce lead: {str(e)}")
            return None


class PipedriveIntegration(BaseCRMIntegration):
    """
    Pipedrive CRM Integration

    Supports:
    - Creating/updating persons
    - Creating organizations
    - Creating deals
    """

    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        self.base_url = "https://api.pipedrive.com/v1"

    async def test_connection(self) -> bool:
        """Test Pipedrive connection"""
        try:
            url = f"{self.base_url}/users/me"
            params = {"api_token": self.api_key}

            async with self.session.get(url, params=params) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Pipedrive connection test failed: {str(e)}")
            return False

    async def create_contact(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create person in Pipedrive"""
        url = f"{self.base_url}/persons"

        data = {
            "name": lead_data.get('contact_name') or lead_data.get('company_name'),
            "email": lead_data.get('email') or lead_data.get('contact_email'),
            "phone": lead_data.get('phone') or lead_data.get('contact_phone'),
            "org_name": lead_data.get('company_name'),
            "api_token": self.api_key
        }

        data = {k: v for k, v in data.items() if v is not None}

        try:
            async with self.session.post(url, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    return result.get('data', {})
                else:
                    error_text = await response.text()
                    raise Exception(f"Pipedrive API error: {error_text}")
        except Exception as e:
            logger.error(f"Error creating Pipedrive person: {str(e)}")
            raise

    async def update_contact(self, contact_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update person in Pipedrive"""
        url = f"{self.base_url}/persons/{contact_id}"

        data = {
            "phone": lead_data.get('phone') or lead_data.get('contact_phone'),
            "api_token": self.api_key
        }

        data = {k: v for k, v in data.items() if v is not None}

        try:
            async with self.session.put(url, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', {})
                else:
                    error_text = await response.text()
                    raise Exception(f"Pipedrive API error: {error_text}")
        except Exception as e:
            logger.error(f"Error updating Pipedrive person: {str(e)}")
            raise

    async def find_contact(self, email: str) -> Optional[Dict[str, Any]]:
        """Find person by email in Pipedrive"""
        url = f"{self.base_url}/persons/search"
        params = {
            "term": email,
            "fields": "email",
            "api_token": self.api_key
        }

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    result = await response.json()
                    items = result.get('data', {}).get('items', [])
                    return items[0].get('item') if items else None
                return None
        except Exception as e:
            logger.error(f"Error finding Pipedrive person: {str(e)}")
            return None

    async def create_organization(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create organization in Pipedrive"""
        url = f"{self.base_url}/organizations"

        data = {
            "name": lead_data.get('company_name'),
            "address": lead_data.get('address'),
            "api_token": self.api_key
        }

        data = {k: v for k, v in data.items() if v is not None}

        try:
            async with self.session.post(url, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    return result.get('data', {})
                else:
                    error_text = await response.text()
                    raise Exception(f"Pipedrive API error: {error_text}")
        except Exception as e:
            logger.error(f"Error creating Pipedrive organization: {str(e)}")
            raise


class CRMManager:
    """
    Manages CRM integrations

    Supports multiple CRM systems simultaneously
    """

    def __init__(self):
        self.integrations: Dict[str, BaseCRMIntegration] = {}

    async def add_integration(self, crm_type: str, integration: BaseCRMIntegration):
        """Add CRM integration"""
        await integration.connect()
        self.integrations[crm_type] = integration
        logger.info(f"Added {crm_type} integration")

    async def remove_integration(self, crm_type: str):
        """Remove CRM integration"""
        if crm_type in self.integrations:
            await self.integrations[crm_type].disconnect()
            del self.integrations[crm_type]
            logger.info(f"Removed {crm_type} integration")

    async def sync_lead_to_all(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync lead to all connected CRMs"""
        results = {}

        for crm_type, integration in self.integrations.items():
            try:
                result = await integration.sync_lead(lead_data)
                results[crm_type] = {"success": True, "data": result}
            except Exception as e:
                results[crm_type] = {"success": False, "error": str(e)}
                logger.error(f"Error syncing to {crm_type}: {str(e)}")

        return results

    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all CRM connections"""
        results = {}

        for crm_type, integration in self.integrations.items():
            results[crm_type] = await integration.test_connection()

        return results
