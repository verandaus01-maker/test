import { useState, useEffect } from 'react'
import './App.css'
import { api } from './api'

interface Lead {
  company_name: string;
  address: string;
  phone?: string;
  website?: string;
  rating?: number;
  distance_from_center_km?: number;
  decision_makers?: any;
  website_audit?: any;
  outreach_email?: string;
}

function App() {
  const [activeTab, setActiveTab] = useState('scraping')
  const [businessType, setBusinessType] = useState('dental clinics')
  const [city, setCity] = useState('Mumbai')
  const [radiusKm, setRadiusKm] = useState(5)
  const [maxResults, setMaxResults] = useState(10)
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<Lead[]>([])
  const [enrichedLeads, setEnrichedLeads] = useState<any[]>([])
  const [selectedLead, setSelectedLead] = useState<any>(null)
  const [businessTypes, setBusinessTypes] = useState<any[]>([])
  const [showEnrichModal, setShowEnrichModal] = useState(false)

  // Fetch business types on mount
  useEffect(() => {
    loadBusinessTypes()
  }, [])

  const loadBusinessTypes = async () => {
    try {
      const data = await api.getBusinessTypes()
      setBusinessTypes(data.business_types || [])
    } catch (error) {
      console.error('Failed to load business types:', error)
    }
  }

  const handleScrape = async () => {
    setIsLoading(true)
    setResults([])
    setEnrichedLeads([])

    try {
      const data = await api.scrapeIndianBusinesses({
        business_type: businessType,
        city: city,
        radius_km: radiusKm,
        max_results: maxResults,
        sources: ['google_maps', 'justdial']
      })

      setResults(data.leads || [])
      alert(`Found ${data.total_found} businesses!`)
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleBulkEnrich = async () => {
    setIsLoading(true)

    try {
      const data = await api.bulkScrapeAndEnrich({
        business_type: businessType,
        city: city,
        radius_km: radiusKm,
        max_results: Math.min(maxResults, 10), // Limit to 10 for enrichment
        sources: ['google_maps', 'justdial']
      })

      setEnrichedLeads(data.leads || [])
      setActiveTab('enriched')
      alert(`Enriched ${data.total_enriched} leads with website audits and outreach emails!`)
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEnrichSingle = async (lead: Lead) => {
    if (!lead.website) {
      alert('This business has no website to audit')
      return
    }

    setIsLoading(true)

    try {
      const data = await api.enrichLead({
        company_name: lead.company_name,
        website: lead.website,
        find_decision_makers: true,
        audit_website: true,
        generate_lead_magnet: true
      })

      setSelectedLead(data)
      setShowEnrichModal(true)
    } catch (error: any) {
      alert(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold">🇮🇳 Indian Lead Scraper Pro</h1>
              <p className="text-blue-100 mt-1">Advanced lead generation for Indian businesses</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-blue-100">Powered by AI</div>
              <div className="text-xs text-blue-200">Google Maps • JustDial • IndiaMART</div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {['scraping', 'results', 'enriched'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
                {tab === 'results' && results.length > 0 && ` (${results.length})`}
                {tab === 'enriched' && enrichedLeads.length > 0 && ` (${enrichedLeads.length})`}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'scraping' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                🎯 Find Indian Business Leads
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Business Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Type
                  </label>
                  <select
                    value={businessType}
                    onChange={(e) => setBusinessType(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {businessTypes.length > 0 ? (
                      businessTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))
                    ) : (
                      <>
                        <option value="dental clinics">Dental Clinics</option>
                        <option value="restaurants">Restaurants</option>
                        <option value="hotels">Hotels</option>
                        <option value="gyms">Gyms & Fitness Centers</option>
                        <option value="salons">Beauty Salons & Spas</option>
                        <option value="doctors">Doctors & Clinics</option>
                        <option value="lawyers">Law Firms</option>
                        <option value="accountants">Accountants</option>
                        <option value="real estate">Real Estate Agencies</option>
                        <option value="schools">Schools</option>
                      </>
                    )}
                  </select>
                </div>

                {/* City */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    City
                  </label>
                  <select
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                    <option value="Bangalore">Bangalore</option>
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Chennai">Chennai</option>
                    <option value="Kolkata">Kolkata</option>
                    <option value="Pune">Pune</option>
                    <option value="Ahmedabad">Ahmedabad</option>
                    <option value="Jaipur">Jaipur</option>
                    <option value="Surat">Surat</option>
                    <option value="Lucknow">Lucknow</option>
                    <option value="Kanpur">Kanpur</option>
                    <option value="Nagpur">Nagpur</option>
                    <option value="Indore">Indore</option>
                    <option value="Bhopal">Bhopal</option>
                    <option value="Coimbatore">Coimbatore</option>
                    <option value="Chandigarh">Chandigarh</option>
                  </select>
                </div>

                {/* Radius */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Search Radius (km)
                  </label>
                  <input
                    type="number"
                    value={radiusKm}
                    onChange={(e) => setRadiusKm(parseInt(e.target.value))}
                    min="1"
                    max="50"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Find businesses within {radiusKm}km radius
                  </p>
                </div>

                {/* Max Results */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Results
                  </label>
                  <input
                    type="number"
                    value={maxResults}
                    onChange={(e) => setMaxResults(parseInt(e.target.value))}
                    min="1"
                    max="100"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-8 flex space-x-4">
                <button
                  onClick={handleScrape}
                  disabled={isLoading}
                  className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? '🔄 Scraping...' : '🔍 Find Leads'}
                </button>

                <button
                  onClick={handleBulkEnrich}
                  disabled={isLoading}
                  className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? '⚡ Processing...' : '⚡ Scrape + Audit + Generate Emails'}
                </button>
              </div>

              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">💡 What You Get:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>✓ Company name, address, phone, website</li>
                  <li>✓ CEO & Marketing Manager contact details</li>
                  <li>✓ Automatic website audit with scores</li>
                  <li>✓ Personalized outreach email for each lead</li>
                  <li>✓ Lead magnet suggestions to pitch</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'results' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                📊 Scraped Leads ({results.length})
              </h2>

              {results.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p>No results yet. Start by scraping some leads!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {results.map((lead, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {lead.company_name}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">{lead.address}</p>

                          <div className="mt-3 flex flex-wrap gap-3 text-sm">
                            {lead.phone && (
                              <span className="flex items-center text-gray-700">
                                📞 {lead.phone}
                              </span>
                            )}
                            {lead.website && (
                              <a
                                href={lead.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center text-blue-600 hover:underline"
                              >
                                🌐 Website
                              </a>
                            )}
                            {lead.rating && (
                              <span className="flex items-center text-yellow-600">
                                ⭐ {lead.rating}
                              </span>
                            )}
                            {lead.distance_from_center_km && (
                              <span className="text-gray-500">
                                📍 {lead.distance_from_center_km.toFixed(1)} km away
                              </span>
                            )}
                          </div>
                        </div>

                        {lead.website && (
                          <button
                            onClick={() => handleEnrichSingle(lead)}
                            disabled={isLoading}
                            className="ml-4 px-4 py-2 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 disabled:opacity-50"
                          >
                            {isLoading ? '...' : '⚡ Enrich & Audit'}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'enriched' && (
          <div className="space-y-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                ✨ Enriched Leads - Ready for Outreach ({enrichedLeads.length})
              </h2>

              {enrichedLeads.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <p>No enriched leads yet. Use "Scrape + Audit + Generate Emails" button!</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {enrichedLeads.map((lead, index) => (
                    <div key={index} className="border-2 border-purple-200 rounded-lg p-6 bg-gradient-to-r from-purple-50 to-indigo-50">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">
                            {lead.company_name}
                          </h3>
                          <p className="text-sm text-gray-600">{lead.address}</p>
                        </div>

                        {lead.website_audit && (
                          <div className="text-right">
                            <div className="text-3xl font-bold text-purple-600">
                              {lead.website_audit.overall_score || 'N/A'}
                            </div>
                            <div className="text-xs text-gray-600">Website Score</div>
                          </div>
                        )}
                      </div>

                      {/* Website Audit Summary */}
                      {lead.website_audit && (
                        <div className="bg-white rounded-lg p-4 mb-4">
                          <h4 className="font-semibold text-gray-900 mb-2">🔍 Website Audit:</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                            <div>
                              <span className="text-gray-600">Critical Issues:</span>
                              <span className="ml-2 font-semibold text-red-600">
                                {lead.website_audit.critical_issues_count || 0}
                              </span>
                            </div>
                            <div>
                              <span className="text-gray-600">Opportunities:</span>
                              <span className="ml-2 font-semibold text-green-600">
                                {lead.website_audit.opportunities?.length || 0}
                              </span>
                            </div>
                          </div>

                          {lead.website_audit.opportunities && lead.website_audit.opportunities.length > 0 && (
                            <div className="mt-3 space-y-2">
                              {lead.website_audit.opportunities.slice(0, 3).map((opp: any, i: number) => (
                                <div key={i} className="text-sm text-gray-700 pl-4 border-l-2 border-purple-400">
                                  <strong>{opp.title}:</strong> {opp.pitch_angle}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Outreach Email */}
                      {lead.outreach_email && (
                        <div className="bg-white rounded-lg p-4">
                          <h4 className="font-semibold text-gray-900 mb-2">📧 Personalized Outreach Email:</h4>
                          <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto">
                            {lead.outreach_email}
                          </pre>

                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(lead.outreach_email)
                              alert('Email copied to clipboard!')
                            }}
                            className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                          >
                            📋 Copy Email
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Enrichment Modal */}
      {showEnrichModal && selectedLead && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-2xl font-bold text-gray-900">
                Enrichment Results - {selectedLead.company_name}
              </h2>
              <button
                onClick={() => setShowEnrichModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* Decision Makers */}
            {selectedLead.decision_makers && (
              <div className="mb-6">
                <h3 className="font-semibold text-lg mb-2">👥 Decision Makers:</h3>
                {selectedLead.decision_makers.email_patterns && (
                  <div className="bg-gray-50 p-4 rounded">
                    <p className="text-sm font-medium mb-2">Likely Email Patterns:</p>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries(selectedLead.decision_makers.email_patterns).map(([role, emails]: [string, any]) => (
                        <div key={role}>
                          <strong>{role}:</strong>
                          <ul className="pl-4">
                            {emails.slice(0, 2).map((email: string, i: number) => (
                              <li key={i} className="text-gray-600">{email}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Website Audit */}
            {selectedLead.website_audit && (
              <div className="mb-6">
                <h3 className="font-semibold text-lg mb-2">🔍 Website Audit:</h3>
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded">
                  <div className="text-center mb-4">
                    <div className="text-4xl font-bold text-purple-600">
                      {selectedLead.website_audit.overall_score}/100
                    </div>
                    <div className="text-sm text-gray-600">Overall Score</div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    {Object.entries(selectedLead.website_audit.scores || {}).map(([category, score]: [string, any]) => (
                      <div key={category} className="text-center bg-white p-2 rounded">
                        <div className="font-bold text-lg">{score}</div>
                        <div className="text-xs text-gray-600 capitalize">{category.replace('_', ' ')}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Outreach Email */}
            {selectedLead.outreach_email_template && (
              <div>
                <h3 className="font-semibold text-lg mb-2">📧 Outreach Email:</h3>
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-gray-50 p-4 rounded border border-gray-200">
                  {selectedLead.outreach_email_template}
                </pre>
              </div>
            )}

            <button
              onClick={() => setShowEnrichModal(false)}
              className="mt-6 w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
