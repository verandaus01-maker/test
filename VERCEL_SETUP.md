# 🚀 Vercel Deployment - IMPORTANT Setup Steps

## ⚠️ CRITICAL: You Must Configure These Settings in Vercel Dashboard

The 404 error happens because Vercel needs to know your frontend is in a subdirectory.

---

## 📋 Step-by-Step Setup:

### 1. Go to Your Vercel Project Settings

After importing your repository to Vercel:

1. Click on your project
2. Go to **Settings** tab
3. Go to **General** section

### 2. Configure Build & Development Settings

Scroll down to **Build & Development Settings** and configure:

#### Root Directory
```
frontend
```
**IMPORTANT:** Click "Edit" next to "Root Directory" and enter `frontend`

This tells Vercel where your React app is located.

#### Build Command (Auto-detected, but verify)
```
npm run build
```

#### Output Directory (Auto-detected, but verify)
```
dist
```

#### Install Command (Auto-detected)
```
npm install
```

### 3. Add Environment Variables

Still in Settings, go to **Environment Variables** section:

Add this variable:
```
Name: VITE_API_URL
Value: https://your-backend-url.com
```

(You'll update this after deploying the backend)

### 4. Save and Redeploy

1. Click **Save**
2. Go to **Deployments** tab
3. Click the three dots (...) on the latest deployment
4. Click **Redeploy**

---

## ✅ What Should Happen:

After configuration:
- Vercel will build from the `frontend` directory
- Output will come from `frontend/dist`
- Your React app should load at `https://your-project.vercel.app`

---

## 🔍 Verification Checklist:

After redeployment, check:
- [ ] Root Directory is set to `frontend` in Vercel settings
- [ ] Build succeeds (check deployment logs)
- [ ] Homepage loads (no 404)
- [ ] React app appears

---

## 🐛 Still Getting 404?

### Check Deployment Logs:
1. Go to **Deployments** tab
2. Click on the latest deployment
3. Check **Build Logs**
4. Look for errors

### Common Issues:

**Issue:** "npm: command not found"
- **Fix:** Make sure Root Directory is set to `frontend`

**Issue:** "Cannot find module 'react'"
- **Fix:** Deployment should install dependencies automatically. Check if `frontend/package.json` exists

**Issue:** "Build failed"
- **Fix:** Check if `frontend/src/main.tsx` and `frontend/src/App.tsx` exist

---

## 📦 Project Structure (for reference):

```
/
├── backend/              # Python FastAPI (deploy separately)
├── frontend/             # React app (deploy to Vercel)
│   ├── src/
│   │   ├── main.tsx
│   │   └── App.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── vercel.json           # Vercel configuration
└── package.json          # Root package file
```

---

## 🎯 Quick Summary:

**Why This is Needed:**
- Your repository has both backend (Python) and frontend (React)
- They're in separate directories
- Vercel needs to know to ONLY build the `frontend` directory
- Setting "Root Directory" to `frontend` solves this

**After This Setup:**
- ✅ Vercel builds correctly
- ✅ No more 404 errors
- ✅ React app loads properly

---

## 🔗 Next Steps After Frontend Works:

1. Deploy backend to Railway/Render (see DEPLOYMENT.md)
2. Get backend URL
3. Update `VITE_API_URL` environment variable in Vercel
4. Redeploy frontend

---

## 📞 Need Help?

If still having issues:
1. Check Vercel build logs (Deployments > Latest > View Function Logs)
2. Verify Root Directory setting is exactly `frontend` (no trailing slash)
3. Make sure the repository is up to date
4. Try a manual redeploy

---

**Remember:** The key setting is **Root Directory = frontend** in Vercel dashboard!
