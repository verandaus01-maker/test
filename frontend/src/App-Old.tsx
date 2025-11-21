import { useState } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Lead Scraper Pro</h1>
              <span className="ml-3 px-2 py-1 text-xs font-semibold text-primary-700 bg-primary-100 rounded-full">
                Enterprise
              </span>
            </div>
            <nav className="hidden md:flex space-x-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'dashboard'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('leads')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'leads'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Leads
              </button>
              <button
                onClick={() => setActiveTab('scraping')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'scraping'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Scraping
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  activeTab === 'analytics'
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Analytics
              </button>
            </nav>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-500 hover:text-gray-700">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
                  A
                </div>
                <span className="text-sm font-medium text-gray-700">Admin</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'leads' && <LeadsView />}
        {activeTab === 'scraping' && <ScrapingView />}
        {activeTab === 'analytics' && <AnalyticsView />}
      </main>
    </div>
  )
}

function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Total Leads" value="12,458" change="+12.5%" positive />
        <StatCard title="High Quality" value="3,842" change="+8.2%" positive />
        <StatCard title="Active Campaigns" value="24" change="+3" positive />
        <StatCard title="Avg Lead Score" value="78.5" change="+5.3%" positive />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ActionButton icon="🎯" title="New Scraping Job" />
          <ActionButton icon="📤" title="Export Leads" />
          <ActionButton icon="🔄" title="Sync to CRM" />
          <ActionButton icon="📧" title="Email Campaign" />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <ActivityItem title="Scraping job completed" description="LinkedIn - Tech Companies" time="2 minutes ago" />
          <ActivityItem title="348 new leads enriched" description="Email verification completed" time="15 minutes ago" />
          <ActivityItem title="Export generated" description="CSV export ready for download" time="1 hour ago" />
          <ActivityItem title="Campaign sent" description="Follow-up email to 250 leads" time="3 hours ago" />
        </div>
      </div>
    </div>
  )
}

function LeadsView() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Leads</h2>
        <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          Add Lead
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            type="text"
            placeholder="Search leads..."
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option>All Industries</option>
            <option>Technology</option>
            <option>Healthcare</option>
          </select>
          <select className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option>All Scores</option>
            <option>High (80+)</option>
            <option>Medium (50-79)</option>
          </select>
          <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            Advanced Filters
          </button>
        </div>
      </div>

      {/* Leads Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Industry</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <LeadRow
              company="Acme Corp"
              contact="john@acme.com"
              industry="Technology"
              score={92}
              status="New"
            />
            <LeadRow
              company="TechStart Inc"
              contact="sarah@techstart.com"
              industry="Software"
              score={85}
              status="Contacted"
            />
            <LeadRow
              company="Digital Solutions"
              contact="mike@digitalsol.com"
              industry="Marketing"
              score={78}
              status="Qualified"
            />
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ScrapingView() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Scraping Jobs</h2>
        <button className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          New Scraping Job
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <JobCard
          title="LinkedIn Tech Companies"
          status="Running"
          progress={65}
          leads={1250}
          sources={['LinkedIn', 'Company Websites']}
        />
        <JobCard
          title="Google Maps - SF Bay Area"
          status="Completed"
          progress={100}
          leads={3450}
          sources={['Google Maps']}
        />
        <JobCard
          title="Healthcare Providers"
          status="Pending"
          progress={0}
          leads={0}
          sources={['LinkedIn', 'Google Maps']}
        />
      </div>
    </div>
  )
}

function AnalyticsView() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Lead Sources</h3>
          <div className="space-y-3">
            <SourceBar source="LinkedIn" percentage={45} count={5620} />
            <SourceBar source="Google Maps" percentage={30} count={3745} />
            <SourceBar source="Company Websites" percentage={15} count={1873} />
            <SourceBar source="Manual" percentage={10} count={1248} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Lead Quality Distribution</h3>
          <div className="space-y-3">
            <QualityBar quality="High (80+)" percentage={35} count={4369} color="bg-green-500" />
            <QualityBar quality="Medium (50-79)" percentage={45} count={5616} color="bg-yellow-500" />
            <QualityBar quality="Low (<50)" percentage={20} count={2496} color="bg-red-500" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper Components
function StatCard({ title, value, change, positive }: { title: string; value: string; change: string; positive: boolean }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-sm font-medium text-gray-500">{title}</div>
      <div className="mt-2 flex items-baseline">
        <div className="text-2xl font-semibold text-gray-900">{value}</div>
        <span className={`ml-2 text-sm font-medium ${positive ? 'text-green-600' : 'text-red-600'}`}>
          {change}
        </span>
      </div>
    </div>
  )
}

function ActionButton({ icon, title }: { icon: string; title: string }) {
  return (
    <button className="flex flex-col items-center justify-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <span className="text-3xl mb-2">{icon}</span>
      <span className="text-sm font-medium text-gray-700">{title}</span>
    </button>
  )
}

function ActivityItem({ title, description, time }: { title: string; description: string; time: string }) {
  return (
    <div className="flex items-start space-x-3 py-2">
      <div className="w-2 h-2 mt-2 bg-primary-600 rounded-full"></div>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{title}</p>
        <p className="text-sm text-gray-500">{description}</p>
      </div>
      <span className="text-xs text-gray-400">{time}</span>
    </div>
  )
}

function LeadRow({ company, contact, industry, score, status }: any) {
  const scoreColor = score >= 80 ? 'text-green-600 bg-green-100' : score >= 50 ? 'text-yellow-600 bg-yellow-100' : 'text-red-600 bg-red-100'

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4 whitespace-nowrap">
        <div className="font-medium text-gray-900">{company}</div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{contact}</td>
      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{industry}</td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${scoreColor}`}>
          {score}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        <span className="px-2 py-1 text-xs font-semibold text-primary-700 bg-primary-100 rounded-full">
          {status}
        </span>
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
        <button className="text-primary-600 hover:text-primary-900">View</button>
      </td>
    </tr>
  )
}

function JobCard({ title, status, progress, leads, sources }: any) {
  const statusColor = status === 'Running' ? 'bg-blue-100 text-blue-800' : status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColor}`}>
          {status}
        </span>
      </div>
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-500">Progress</span>
          <span className="font-medium">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-primary-600 h-2 rounded-full" style={{ width: `${progress}%` }}></div>
        </div>
      </div>
      <div className="text-sm text-gray-500 mb-2">
        <span className="font-medium text-gray-900">{leads}</span> leads found
      </div>
      <div className="flex flex-wrap gap-1">
        {sources.map((source: string) => (
          <span key={source} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
            {source}
          </span>
        ))}
      </div>
    </div>
  )
}

function SourceBar({ source, percentage, count }: any) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-gray-700">{source}</span>
        <span className="text-gray-500">{count} ({percentage}%)</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className="bg-primary-600 h-2 rounded-full" style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  )
}

function QualityBar({ quality, percentage, count, color }: any) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="font-medium text-gray-700">{quality}</span>
        <span className="text-gray-500">{count} ({percentage}%)</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`${color} h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  )
}

export default App
