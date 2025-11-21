# 🚂 Railway Deployment Guide - Step by Step

Deploy your backend to Railway in **10 minutes**!

---

## Prerequisites

1. Railway account (free): https://railway.app
2. GitHub account connected to Railway
3. Your repository pushed to GitHub ✅ (already done)

---

## Step 1: Create Railway Project

1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select your repository: **`verandaus01-maker/test`**
5. Railway will detect it's a Python project

---

## Step 2: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database"**
3. Choose **"PostgreSQL"**
4. Railway will create a PostgreSQL instance
5. **Important:** Railway automatically sets `DATABASE_URL` environment variable

---

## Step 3: Add Redis Cache

1. Click **"+ New"** again
2. Select **"Database"**
3. Choose **"Redis"**
4. Railway will create a Redis instance
5. **Important:** Railway automatically sets `REDIS_URL` environment variable

---

## Step 4: Configure Environment Variables

1. Click on your **main service** (the Python app, not database/redis)
2. Go to **"Variables"** tab
3. Click **"Raw Editor"**
4. Copy and paste these variables:

```bash
APP_NAME=Lead Scraper Pro
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

SECRET_KEY=change-this-to-random-string-min-32-chars
JWT_SECRET_KEY=change-this-to-another-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=["https://your-vercel-app.vercel.app","http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=true

RATE_LIMIT_PER_MINUTE=60
```

5. **Important:** Change the `SECRET_KEY` and `JWT_SECRET_KEY` to random strings
6. **Important:** Replace `your-vercel-app.vercel.app` with your actual Vercel URL

---

## Step 5: Configure Build Settings

1. Still in your main service, go to **"Settings"** tab
2. Scroll to **"Build"** section
3. Set **Build Command**:
   ```
   cd backend && pip install -r requirements.txt
   ```
4. Set **Start Command**:
   ```
   cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Set **Healthcheck Path**: `/health`

---

## Step 6: Deploy!

1. Click **"Deploy"** or just save changes
2. Railway will automatically:
   - Install dependencies
   - Start your FastAPI server
   - Connect to PostgreSQL and Redis
3. Wait 2-3 minutes for deployment

---

## Step 7: Get Your Backend URL

1. In your Railway project, click on the main service
2. Go to **"Settings"** tab
3. Scroll to **"Networking"** section
4. Click **"Generate Domain"**
5. Railway will give you a URL like: `https://your-app.up.railway.app`
6. **Copy this URL!** You'll need it for frontend

---

## Step 8: Test Backend

1. Open your Railway URL in browser: `https://your-app.up.railway.app`
2. You should see:
   ```json
   {
     "message": "Welcome to Lead Scraper Pro",
     "version": "1.0.0",
     "docs": "/docs",
     "health": "/health"
   }
   ```
3. Test API docs: `https://your-app.up.railway.app/docs`
4. Test health: `https://your-app.up.railway.app/health`

If you see these, **backend is working!** 🎉

---

## Step 9: Connect Frontend to Backend

Now update your Vercel frontend to use the Railway backend:

1. Go to **Vercel Dashboard**
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add/Update:
   ```
   VITE_API_URL=https://your-app.up.railway.app
   ```
   (Use your actual Railway URL)
5. Go to **Deployments** → Click **Redeploy**

---

## Step 10: Test Complete System!

1. Open your Vercel frontend URL
2. Go to **Scraping** tab
3. Try scraping: "Dental Clinics" in "Mumbai"
4. Click **"Scrape + Audit + Generate Emails"**
5. Wait 1-2 minutes
6. Check **"Enriched"** tab for results!

---

## 🎉 You're Live!

Your complete lead scraping system is now deployed:
- ✅ Frontend on Vercel
- ✅ Backend on Railway
- ✅ PostgreSQL database
- ✅ Redis cache
- ✅ Indian business scraping working
- ✅ Website audits working
- ✅ Email generation working

---

## 💡 Important Notes

### Database Initialization

Railway PostgreSQL is empty by default. The app will auto-create tables on first run, but for production you should run migrations:

1. In Railway, go to your main service
2. Click **"Settings"** → **"Deploy Triggers"**
3. Or connect via Railway CLI and run:
   ```bash
   railway run cd backend && alembic upgrade head
   ```

### Cost Estimate

Railway Free Tier includes:
- $5 free credit per month
- After that, approximately:
  - Web service: ~$5/month
  - PostgreSQL: ~$5/month
  - Redis: ~$5/month
- **Total: ~$15/month** (after free credits)

### Monitoring

1. Railway provides logs: Click service → **"Logs"** tab
2. Check for errors in deployment
3. Monitor API requests

---

## 🐛 Troubleshooting

### Issue: "Failed to build"

**Solution:**
1. Check **Logs** tab in Railway
2. Make sure `requirements.txt` is in `backend/` folder
3. Verify build command: `cd backend && pip install -r requirements.txt`

### Issue: "Application error"

**Solution:**
1. Check environment variables are set correctly
2. Make sure `DATABASE_URL` and `REDIS_URL` are present
3. Check logs for specific error

### Issue: "Cannot connect to database"

**Solution:**
1. Make sure PostgreSQL service is running
2. Check that `DATABASE_URL` is automatically set
3. Verify the main service and database are in same project

### Issue: Frontend shows "Network Error"

**Solution:**
1. Check Railway backend URL is correct
2. Verify `CORS_ORIGINS` includes your Vercel URL
3. Test backend URL directly in browser first

---

## 🔐 Security Checklist

Before going live:
- [ ] Changed `SECRET_KEY` to random string (32+ characters)
- [ ] Changed `JWT_SECRET_KEY` to different random string
- [ ] Set `DEBUG=false`
- [ ] Updated `CORS_ORIGINS` with only your Vercel URL
- [ ] Removed `http://localhost:3000` from CORS in production
- [ ] Added Google Maps API key (optional but recommended)
- [ ] Set up monitoring/alerts

---

## 📊 Next Steps

1. **Test thoroughly** with different business types and cities
2. **Monitor usage** in Railway dashboard
3. **Set up Google Maps API key** for better scraping results
4. **Configure email SMTP** for outreach campaigns
5. **Add CRM integrations** (HubSpot, Salesforce) if needed

---

## 🆘 Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check Railway logs for detailed error messages
- Review `backend/app/main.py` for app configuration

---

**Your backend is now live on Railway! 🚀**
