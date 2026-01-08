# 🔧 Manual Database Setup on Render (Step-by-Step)

## If "Link Database" Option is Not Available

Follow these steps to manually set up the database connection:

## Step 1: Get Database Connection Details

1. Go to Render Dashboard
2. Click on your **PostgreSQL database** (`voting-system-db`)
3. In the database dashboard, look for:
   - **"Connection"** tab/section, OR
   - **"Info"** tab/section, OR
   - **"Settings"** tab/section

4. Find and copy the **"Internal Database URL"**
   - ⚠️ Use **Internal** URL, NOT External
   - It should look like: `postgres://user:password@hostname:5432/dbname`

## Step 2: Convert to PostgreSQL Format

If the URL starts with `postgres://`, change it to `postgresql://`:

**Before:** `postgres://user:pass@host:5432/dbname`  
**After:** `postgresql://user:pass@host:5432/dbname`

## Step 3: Add DATABASE_URL to Web Service

1. Go to your **Web Service** dashboard (`blockchain-voting-system`)
2. Click on **"Environment"** tab (in the left sidebar or top menu)
3. Scroll down to see existing environment variables
4. Click **"Add Environment Variable"** button
5. Fill in:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the converted URL (with `postgresql://`)
6. Click **"Save Changes"** or **"Add"**

## Step 4: Verify Environment Variables

Make sure you have these environment variables set:

| Key | Value | Required |
|-----|-------|----------|
| `DATABASE_URL` | `postgresql://...` | ✅ Yes |
| `FLASK_ENV` | `production` | ✅ Yes |
| `SECRET_KEY` | (random string) | ✅ Yes |
| `PYTHON_VERSION` | `3.12.0` or `3.13.4` | Optional |

## Step 5: Redeploy

1. After adding `DATABASE_URL`, go to **"Manual Deploy"** tab
2. Click **"Deploy latest commit"**
3. Watch the build logs

## Step 6: Check Logs

After deployment, check the logs for:

✅ **Success indicators:**
```
[ProductionConfig] Using DATABASE_URL from environment: postgresql://...
Starting database initialization...
Database URI: postgresql://***:***@...
Database tables created successfully
```

❌ **If you still see errors:**
- Check that `DATABASE_URL` is exactly `postgresql://` (not `postgres://`)
- Verify the URL is correct (copy-paste from database dashboard)
- Make sure you used **Internal** URL, not External

## Alternative: Construct URL Manually

If you can't find the full URL, you can build it from components:

1. From database dashboard, note these values:
   - **Host**: `dpg-xxxxx-a.oregon-postgres.render.com` (example)
   - **Port**: `5432` (usually)
   - **Database**: `voting_system` (or your database name)
   - **User**: `voting_user` (or your username)
   - **Password**: (your password)

2. Format: `postgresql://USER:PASSWORD@HOST:PORT/DATABASE`

3. Example:
   ```
   postgresql://voting_user:mypassword@dpg-xxxxx-a.oregon-postgres.render.com:5432/voting_system
   ```

## Troubleshooting

### Can't find Internal Database URL?
- Look in different tabs: Connection, Info, Settings, Overview
- Some databases show it in the main dashboard
- Check if there's a "Show Connection String" button

### URL format issues?
- Must start with `postgresql://` (not `postgres://`)
- No spaces in the URL
- Special characters in password may need URL encoding

### Still getting SQLite errors?
- Double-check `DATABASE_URL` is in environment variables
- Verify `FLASK_ENV=production` is set
- Check logs for the actual database URI being used

## Quick Checklist

- [ ] PostgreSQL database created
- [ ] Found Internal Database URL
- [ ] Converted `postgres://` to `postgresql://`
- [ ] Added `DATABASE_URL` environment variable
- [ ] Verified `FLASK_ENV=production` is set
- [ ] Redeployed after adding variable
- [ ] Checked logs for success messages

Once `DATABASE_URL` is set correctly, your app will connect to PostgreSQL! 🎉

