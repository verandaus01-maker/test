# Deployment Guide

This application consists of two parts that need to be deployed separately:

## 🎨 Frontend Deployment (Vercel)

The frontend is a React application that can be deployed to Vercel.

### Steps:

1. **Connect Repository to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your Git repository

2. **Configure Environment Variables**
   In Vercel project settings, add:
   ```
   VITE_API_URL=https://your-backend-url.com
   ```

3. **Deploy**
   - Vercel will automatically detect the configuration from `vercel.json`
   - The build will run from the `frontend` directory
   - Output will be from `frontend/dist`

### ✅ What's Already Configured:
- `vercel.json` with build commands
- SPA routing fallback
- API proxy configuration
- Security headers

---

## 🚀 Backend Deployment (Python FastAPI)

**IMPORTANT:** The Python backend CANNOT run on Vercel. It requires a platform that supports:
- Long-running Python processes
- PostgreSQL database
- Redis cache
- Background workers (Celery)

### Recommended Platforms:

#### Option 1: Railway (Easiest)
Railway supports Docker and can deploy the entire stack.

**Steps:**
1. Go to [Railway](https://railway.app)
2. Create new project from GitHub repo
3. Add PostgreSQL service
4. Add Redis service
5. Deploy the backend service
6. Set environment variables from `.env.example`

**Cost:** ~$10-20/month with database

---

#### Option 2: Render
Render offers free PostgreSQL and good Python support.

**Steps:**
1. Go to [Render](https://render.com)
2. Create a new Web Service
3. Connect your repository
4. Set build command: `cd backend && pip install -r requirements.txt`
5. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add PostgreSQL database (free tier available)
7. Add Redis service
8. Configure environment variables

**Cost:** Free tier available (with limitations)

---

#### Option 3: AWS/DigitalOcean/Linode (Most Control)
Deploy using Docker Compose for full control.

**Steps:**
1. Create a VPS (Virtual Private Server)
2. Install Docker and Docker Compose
3. Clone repository
4. Copy `.env.example` to `.env` and configure
5. Run: `docker-compose up -d`

**Cost:** ~$5-10/month for basic VPS

---

#### Option 4: Heroku
**Steps:**
1. Create Heroku app
2. Add PostgreSQL and Redis add-ons
3. Set buildpack: `heroku/python`
4. Deploy backend directory

**Cost:** ~$7/month minimum

---

## 📋 Backend Environment Variables

You'll need to set these on your backend hosting platform:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis
REDIS_URL=redis://host:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# API Keys (for scraping features)
LINKEDIN_API_KEY=your-key
GOOGLE_MAPS_API_KEY=your-key
CLEARBIT_API_KEY=your-key

# CRM Integrations
HUBSPOT_API_KEY=your-key
SALESFORCE_CLIENT_ID=your-id
SALESFORCE_CLIENT_SECRET=your-secret
PIPEDRIVE_API_KEY=your-key

# Email (for campaigns)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password
```

---

## 🔗 Connecting Frontend to Backend

After deploying the backend:

1. Get your backend URL (e.g., `https://your-app.railway.app`)
2. Update Vercel environment variable:
   ```
   VITE_API_URL=https://your-app.railway.app
   ```
3. Redeploy frontend on Vercel
4. Update `vercel.json` line 8 with your actual backend URL

---

## 🧪 Testing Deployment

1. **Frontend:** Visit your Vercel URL
2. **Backend:** Visit `https://your-backend-url.com/docs` for API documentation
3. **Health Check:** Visit `https://your-backend-url.com/health`

---

## 🎯 Quick Start Recommendation

**For fastest deployment:**

1. **Backend:** Deploy to Railway (5 minutes)
   - Automatic Docker support
   - Built-in PostgreSQL/Redis
   - Easy environment variables

2. **Frontend:** Deploy to Vercel (2 minutes)
   - Already configured with `vercel.json`
   - Just add backend URL

**Total time:** ~10 minutes

---

## 🔧 Troubleshooting

### Frontend 404 Error
- ✅ Fixed! The `vercel.json` now properly configures the build
- Make sure environment variable `VITE_API_URL` is set

### Backend Connection Error
- Check that backend is deployed and running
- Verify `VITE_API_URL` matches your backend URL
- Check CORS settings in `backend/app/main.py`

### Database Connection Error
- Ensure `DATABASE_URL` is set correctly
- Format: `postgresql://user:password@host:port/database`
- Run migrations: `alembic upgrade head`

---

## 📦 Production Checklist

- [ ] Backend deployed and accessible
- [ ] Database provisioned and connected
- [ ] Redis provisioned and connected
- [ ] Environment variables configured
- [ ] API keys added (LinkedIn, Google Maps, etc.)
- [ ] Frontend deployed to Vercel
- [ ] `VITE_API_URL` points to backend
- [ ] Test scraping functionality
- [ ] Test user authentication
- [ ] Test lead exports
- [ ] Test CRM integrations

---

## 💡 Notes

- The frontend is a static React app (perfect for Vercel)
- The backend needs persistent connections (not suitable for Vercel)
- Database and Redis are required for backend
- Celery workers needed for background scraping jobs
- Consider setting up monitoring (Sentry, LogRocket)

---

For questions, check the main [README.md](./README.md) or open an issue.
