// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Indian Leads
  scrapeIndianBusinesses: '/api/v1/indian-leads/scrape',
  scrapeByRadius: '/api/v1/indian-leads/scrape/radius',
  enrichLead: '/api/v1/indian-leads/enrich',
  bulkScrapeAndEnrich: '/api/v1/indian-leads/bulk-scrape-and-enrich',
  searchCities: '/api/v1/indian-leads/cities/search',
  getBusinessTypes: '/api/v1/indian-leads/business-types',
  verifyEmails: '/api/v1/indian-leads/verify-emails',

  // Auth
  login: '/api/v1/auth/login',
  register: '/api/v1/auth/register',
};
