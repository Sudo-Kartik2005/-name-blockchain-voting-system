# 🚀 Quick Deployment Guide (Free Tier - Manual Method)

## Step-by-Step Instructions

### 1. Push Your Code to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with GitHub (free)

### 3. Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `voting-system-db`
   - **Plan**: **Free**
   - **Region**: Choose closest to you
3. Click **"Create Database"**
4. **Wait for database to be ready** (takes ~1-2 minutes)
5. **Copy the "Internal Database URL"** (you'll need it)

### 4. Create Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. **Connect GitHub** (if not already connected)
3. **Select your repository**: `your-username/blockchain-voting-system`
4. Configure the service:

   **Basic Settings:**
   - **Name**: `blockchain-voting-system` (or any name you prefer)
   - **Region**: Same as database
   - **Branch**: `main` (or your main branch)
   - **Root Directory**: (leave empty)
   - **Environment**: **Python 3**
   - **Plan**: **Free**

   **Build & Deploy:**
   - **Build Command**: 
     ```
     pip install --upgrade pip && pip install -r requirements-prod.txt
     ```
   - **Start Command**: 
     ```
     gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 60 --access-logfile - --error-logfile - wsgi:application
     ```

5. Click **"Create Web Service"**

### 5. Link Database to Web Service

1. In your **Web Service** dashboard
2. Go to **"Environment"** tab
3. Scroll down to **"Link Database"** section
4. Click **"Link Database"**
5. Select your `voting-system-db` database
6. This automatically sets `DATABASE_URL` environment variable ✅

### 6. Set Environment Variables

Still in **"Environment"** tab, click **"Add Environment Variable"** for each:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Click **"Generate"** button (or use a secure random string) |
| `PYTHON_VERSION` | `3.12.0` |
| `BLOCKCHAIN_MINING_INTERVAL` | `10` |

**Note**: `DATABASE_URL` is automatically set when you link the database - don't add it manually!

### 7. Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Watch the build logs
3. Wait for deployment to complete (~3-5 minutes)

### 8. Verify Deployment

1. **Check Build Logs:**
   - Look for "Build successful"
   - No errors in red

2. **Check Runtime Logs:**
   - Switch to "Logs" tab
   - Look for "Application startup complete"
   - Should see "Database initialization completed successfully"

3. **Test Health Endpoint:**
   - Your app URL: `https://blockchain-voting-system.onrender.com`
   - Visit: `https://your-app-name.onrender.com/health`
   - Should return: `{"status": "healthy", "database": "connected"}`

## ✅ Success Checklist

- [ ] Database created and running
- [ ] Web service created
- [ ] Database linked to web service
- [ ] Environment variables set
- [ ] Build successful
- [ ] Health check returns 200 OK
- [ ] App accessible via Render URL

## 🐛 Common Issues

### Build Fails
- Check `requirements-prod.txt` exists
- Verify Python version is 3.12.0
- Check build logs for specific errors

### Database Connection Error
- Verify database is linked in Environment tab
- Check `DATABASE_URL` is set (should be automatic)
- Ensure database is running (not paused)

### App Won't Start
- Check start command is correct
- Verify `wsgi.py` exists
- Check runtime logs for errors

## 📝 Important Notes

- **Free tier limitations:**
  - Services spin down after 15 minutes of inactivity
  - First request after spin-down takes ~30 seconds
  - Database has 90-day free trial, then requires paid plan

- **render.yaml is NOT used** in manual deployment (it's only for Blueprint/paid tier)

- **Auto-deploy**: Enabled by default - pushes to main branch will auto-deploy

## 🎉 You're Done!

Your app should now be live at: `https://your-app-name.onrender.com`

Test it:
- Visit `/health` - should return healthy status
- Visit `/` - should show home page
- Visit `/register` - should show registration form

