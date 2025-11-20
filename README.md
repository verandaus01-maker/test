# Advanced Lead Scraping System

An enterprise-grade lead generation and scraping platform built for digital marketing agencies. This system provides multi-source data collection, AI-powered lead scoring, advanced filtering, and seamless CRM integrations.

## Features

### Core Capabilities
- **Multi-Source Scraping**: LinkedIn, Google Maps, industry directories, company websites
- **Advanced Filtering**: 20+ filter types with Boolean logic
- **AI Lead Scoring**: Machine learning-based lead prioritization
- **Data Enrichment**: Automatic email finding, phone validation, firmographic data
- **Technology Detection**: Identify what tools and platforms companies use
- **Real-time & Scheduled Scraping**: On-demand or automated data collection

### Enterprise Features
- **Team Collaboration**: Role-based access control (Admin, Manager, User)
- **RESTful API**: Full API access with authentication
- **CRM Integration**: HubSpot, Salesforce, Pipedrive connectors
- **Export Formats**: CSV, Excel, JSON, XML
- **Webhook Notifications**: Real-time event notifications
- **Compliance**: GDPR and CCPA compliant by design

### Advanced Filtering System
- Industry & sub-industry targeting
- Company size (employees, revenue)
- Geographic targeting (country, state, city, radius-based)
- Technology stack filters
- Growth signals (hiring, funding, news)
- Intent signals (job postings, recent investments)
- Custom Boolean queries
- Domain filters (include/exclude)
- Social media presence requirements
- Funding status and amount

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache & Queue**: Redis
- **Task Processing**: Celery with Redis broker
- **Scraping**: Playwright, Scrapy, Beautiful Soup
- **AI/ML**: scikit-learn, OpenAI API, spaCy

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: React Query

### DevOps
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: pytest, Jest

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

#### Using Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd lead-scraping-system

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Create superuser
docker-compose exec backend python -m app.scripts.create_superuser
```

#### Manual Installation
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# In a new terminal - Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# In another terminal - Start Celery beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info

# Frontend setup (in a new terminal)
cd frontend
npm install
npm run dev
```

### Environment Configuration

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/leadscraperdb

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (optional but recommended)
OPENAI_API_KEY=your-openai-key
HUNTER_IO_API_KEY=your-hunter-key
CLEARBIT_API_KEY=your-clearbit-key

# Scraping Configuration
MAX_CONCURRENT_SCRAPERS=5
PROXY_ENABLED=false
PROXY_ROTATION_URL=

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

## Usage

### Web Dashboard
Access the dashboard at `http://localhost:3000`

1. **Create a Scraping Campaign**
   - Define your target criteria
   - Apply advanced filters
   - Set data enrichment options
   - Schedule or run immediately

2. **View & Manage Leads**
   - Browse collected leads
   - Apply filters and sorting
   - View AI lead scores
   - Enrich individual leads

3. **Export & Integration**
   - Export to CSV, Excel, JSON
   - Push to CRM systems
   - Set up webhooks

### API Usage

```python
import requests

# Authenticate
response = requests.post('http://localhost:8000/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Create scraping job
headers = {'Authorization': f'Bearer {token}'}
job = requests.post('http://localhost:8000/api/scraping/jobs',
    headers=headers,
    json={
        'name': 'Tech Startups in California',
        'sources': ['linkedin', 'google_maps'],
        'filters': {
            'industry': ['Technology', 'Software'],
            'location': {'state': 'California'},
            'company_size': {'min': 10, 'max': 500},
            'technologies': ['React', 'Python']
        }
    }
)

# Get leads
leads = requests.get('http://localhost:8000/api/leads',
    headers=headers,
    params={'job_id': job.json()['id']}
)
```

## Architecture

```
┌─────────────────┐
│   React UI      │
└────────┬────────┘
         │
┌────────▼────────────────────────────────────┐
│          FastAPI Backend                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │   API    │  │  Models  │  │  Auth    │ │
│  └──────────┘  └──────────┘  └──────────┘ │
└────────┬────────────────────────────────────┘
         │
┌────────▼─────────────────────────┐
│      Celery Workers              │
│  ┌────────────┐  ┌─────────────┐│
│  │  Scrapers  │  │  Enrichers  ││
│  └────────────┘  └─────────────┘│
└──────────────────────────────────┘
         │
    ┌────┴─────┬──────────┬──────────┐
    │          │          │          │
┌───▼───┐ ┌───▼────┐ ┌───▼────┐ ┌──▼────┐
│ Scraper│ │LinkedIn│ │ Google │ │ Other │
│ Engine│ │  API   │ │  Maps  │ │Sources│
└───────┘ └────────┘ └────────┘ └───────┘
```

## Project Structure

```
lead-scraping-system/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── leads.py
│   │   │   ├── scraping.py
│   │   │   └── integrations.py
│   │   ├── core/             # Core configuration
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/           # Database models
│   │   │   ├── user.py
│   │   │   ├── lead.py
│   │   │   └── scraping_job.py
│   │   ├── scrapers/         # Scraping modules
│   │   │   ├── base.py
│   │   │   ├── linkedin.py
│   │   │   ├── google_maps.py
│   │   │   └── website.py
│   │   ├── enrichers/        # Data enrichment
│   │   │   ├── email_finder.py
│   │   │   ├── company_data.py
│   │   │   └── tech_stack.py
│   │   ├── filters/          # Filtering engine
│   │   │   └── advanced_filters.py
│   │   ├── scoring/          # Lead scoring AI
│   │   │   └── ml_scorer.py
│   │   ├── integrations/     # CRM integrations
│   │   │   ├── hubspot.py
│   │   │   └── salesforce.py
│   │   └── workers/          # Celery tasks
│   │       └── celery_app.py
│   ├── alembic/              # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── tsconfig.json
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## Security

- JWT-based authentication
- Role-based access control (RBAC)
- Rate limiting on all endpoints
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection
- CORS configuration
- Secrets management via environment variables
- Encrypted data storage for sensitive information

## Compliance

- **GDPR Compliant**: Data export, deletion, and consent management
- **CCPA Compliant**: Consumer data rights
- **Rate Limiting**: Respects website robots.txt and rate limits
- **Data Retention**: Configurable retention policies
- **Audit Logs**: Complete activity tracking

## Performance

- Async/await throughout for non-blocking operations
- Connection pooling for database and Redis
- Celery for distributed task processing
- Caching strategy for frequently accessed data
- Pagination for large result sets
- Efficient database indexing

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Proprietary - All rights reserved

## Support

For support and questions:
- Email: support@yourcompany.com
- Documentation: https://docs.yourcompany.com
- Issues: GitHub Issues

## Roadmap

- [ ] LinkedIn Sales Navigator integration
- [ ] Chrome extension for manual lead capture
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics and reporting
- [ ] AI-powered email template generator
- [ ] Predictive lead scoring v2.0
- [ ] Integration with more CRM platforms
- [ ] Multi-language support
