// API Client Functions
import { API_BASE_URL, API_ENDPOINTS } from './config';

export interface ScrapingRequest {
  business_type: string;
  city: string;
  state?: string;
  radius_km?: number;
  max_results?: number;
  sources?: string[];
}

export interface RadiusSearchRequest {
  business_type: string;
  center_address: string;
  radius_km?: number;
  max_results?: number;
}

export interface EnrichmentRequest {
  company_name: string;
  website?: string;
  find_decision_makers?: boolean;
  audit_website?: boolean;
  generate_lead_magnet?: boolean;
}

class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API Request Error:', error);
      throw error;
    }
  }

  // Indian Leads Endpoints

  async scrapeIndianBusinesses(request: ScrapingRequest) {
    return this.request(API_ENDPOINTS.scrapeIndianBusinesses, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async scrapeByRadius(request: RadiusSearchRequest) {
    return this.request(API_ENDPOINTS.scrapeByRadius, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async enrichLead(request: EnrichmentRequest) {
    return this.request(API_ENDPOINTS.enrichLead, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async bulkScrapeAndEnrich(request: ScrapingRequest) {
    return this.request(API_ENDPOINTS.bulkScrapeAndEnrich, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async searchCities(query: string) {
    return this.request(`${API_ENDPOINTS.searchCities}?query=${encodeURIComponent(query)}`);
  }

  async getBusinessTypes() {
    return this.request(API_ENDPOINTS.getBusinessTypes);
  }

  async verifyEmails(emails: string[]) {
    return this.request(API_ENDPOINTS.verifyEmails, {
      method: 'POST',
      body: JSON.stringify(emails),
    });
  }
}

export const api = new APIClient();
