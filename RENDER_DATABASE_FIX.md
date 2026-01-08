# 🔧 Fix: Database Connection Issue on Render

## Problem
The app is trying to use SQLite instead of PostgreSQL, causing `sqlite3.OperationalError: unable to open database file`.

## Root Cause
The `DATABASE_URL` environment variable is not set or the database is not linked to the web service.

## Solution

### Step 1: Verify Database is Created
1. Go to Render Dashboard
2. Check if you have a PostgreSQL database named `voting-system-db`
3. If not, create it:
   - Click "New +" → "PostgreSQL"
   - Name: `voting-system-db`
   - Plan: Free
   - Click "Create Database"

### Step 2: Set DATABASE_URL Manually (If "Link Database" option is not available)

**Option A: Manual Environment Variable Setup**

1. Go to your **PostgreSQL Database** dashboard (`voting-system-db`)
2. Find the **"Connection"** or **"Info"** section
3. Copy the **"Internal Database URL"** (NOT External URL)
   - It should look like: `postgres://user:password@hostname:port/dbname`
   - Or: `postgresql://user:password@hostname:port/dbname`
4. Go to your **Web Service** dashboard
5. Click on **"Environment"** tab
6. Click **"Add Environment Variable"**
7. Set:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL you copied
8. **Important**: If the URL starts with `postgres://`, change it to `postgresql://`
   - Example: `postgres://...` → `postgresql://...`
9. Click **"Save Changes"**

**Option B: Using Connection String Components**

If you can't find the full URL, you can construct it manually:

1. From your PostgreSQL database dashboard, note:
   - **Host**: (internal hostname)
   - **Port**: (usually 5432)
   - **Database**: (database name)
   - **User**: (username)
   - **Password**: (password)

2. Format: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

3. Add as environment variable `DATABASE_URL` with this value

### Step 3: Verify DATABASE_URL is Set
1. In your **Web Service** → **"Environment"** tab
2. Look for `DATABASE_URL` in the environment variables list
3. It should show something like: `postgresql://user:pass@host:port/dbname`
4. Make sure it starts with `postgresql://` (not `postgres://`)

### Step 4: Alternative - Link Database (if option appears)
Some Render accounts have a "Link Database" option:
1. Go to **Web Service** → **"Environment"** tab
2. Scroll down to **"Link Database"** section (if visible)
3. Click **"Link Database"**
4. Select your `voting-system-db` database

If this option is not available, use Option A above.

1. Go to your **PostgreSQL database** dashboard
2. Copy the **"Internal Database URL"** (not External)
3. Go back to **Web Service** → **Environment** tab
4. Click **"Add Environment Variable"**
5. Key: `DATABASE_URL`
6. Value: Paste the Internal Database URL
7. **Important**: If it starts with `postgres://`, change it to `postgresql://`

### Step 5: Redeploy
1. After linking/adding DATABASE_URL
2. Go to **"Manual Deploy"** → **"Deploy latest commit"**
3. Or wait for auto-deploy (if enabled)

## Verification

After redeploy, check the logs for:
- ✅ `[ProductionConfig] Using DATABASE_URL from environment: postgresql://...`
- ✅ `Database tables created successfully`
- ❌ Should NOT see: `WARNING: DATABASE_URL not set!`

## Common Issues

### Issue: "Database not found" when linking
- Make sure database is fully created (not still provisioning)
- Wait 1-2 minutes after creating database before linking

### Issue: "Connection refused" errors
- Use **Internal Database URL**, not External
- Internal URL is only accessible from within Render's network

### Issue: Still using SQLite after linking
- Check that `FLASK_ENV=production` is set
- Verify `DATABASE_URL` appears in environment variables
- Try manual redeploy after linking

## Quick Checklist

- [ ] PostgreSQL database created
- [ ] Database is running (not paused)
- [ ] Database linked to web service
- [ ] `DATABASE_URL` appears in environment variables
- [ ] `FLASK_ENV=production` is set
- [ ] Redeployed after linking database

## After Fix

Once fixed, you should see in logs:
```
[ProductionConfig] Using DATABASE_URL from environment: postgresql://...
Starting database initialization...
Database URI: postgresql://***:***@...
Database tables created successfully
```

Your app should now connect to PostgreSQL successfully! 🎉

