# Fix "Invalid Username or Password" Issue

## Quick Diagnosis Steps on Render

### Step 1: Access Render Shell

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Open your **Web Service**
3. Click **"Shell"** tab (or "Console")

### Step 2: Run Diagnostic Script

In the Shell, run:

```bash
python test_login.py
```

This will:
- List all users in the database
- Show if admin user exists
- Create admin if it doesn't exist
- Test the login credentials

### Step 3: Create Admin Manually (if needed)

If the script shows no admin user, run:

```bash
python create_admin.py
```

Or run this Python code directly in the shell:

```python
from app_factory import create_app
from models import Voter, db
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()
with app.app_context():
    username = 'newadmin'
    password = '123456'
    
    # Check if exists
    existing = Voter.query.filter_by(username=username).first()
    if existing:
        existing.is_admin = True
        existing.is_active = True
        existing.password_hash = generate_password_hash(password)
        db.session.commit()
        print(f"✅ Updated '{username}' to admin")
    else:
        admin = Voter(
            username=username,
            email='admin@votingsystem.com',
            password_hash=generate_password_hash(password),
            first_name='Admin',
            last_name='User',
            date_of_birth=datetime(1990, 1, 1).date(),
            voter_id='ADMIN001',
            is_admin=True,
            is_verified=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Created admin '{username}'")
    
    # Verify
    from werkzeug.security import check_password_hash
    admin = Voter.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password_hash, password):
        print(f"\n✅ VERIFIED! Login credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
    else:
        print("❌ Verification failed!")
```

### Step 4: Test Login Script

Test specific credentials:

```bash
python test_login.py test newadmin 123456
```

### Step 5: Check Logs for Errors

1. In Render Dashboard, go to **"Logs"** tab
2. Look for print statements from login attempts:
   - `Login attempt for username: ...`
   - `User found: ...`
   - `Password check failed for user: ...`

### Step 6: Verify User Exists

List all users to verify:

```bash
python test_login.py list
```

## Common Issues

### Issue 1: No Admin User Exists
**Solution**: Run `python create_admin.py` or use the manual Python code above.

### Issue 2: User Exists But Password Doesn't Match
**Solution**: The password hash might be wrong. Run the create script again to reset it.

### Issue 3: User Exists But `is_active = False`
**Solution**: Run this in shell:

```python
from app_factory import create_app
from models import Voter, db

app = create_app()
with app.app_context():
    admin = Voter.query.filter_by(username='newadmin').first()
    if admin:
        admin.is_active = True
        admin.is_admin = True
        db.session.commit()
        print("✅ Activated admin user")
```

### Issue 4: Case Sensitivity
Make sure you're using:
- Username: `newadmin` (lowercase)
- Password: `123456` (numbers only)

## Default Admin Credentials

After running the create script:

- **Username**: `newadmin`
- **Password**: `123456`
- **Login URL**: `https://your-app-name.onrender.com/login`

## Still Not Working?

1. **Check Render Logs** - Look for error messages
2. **Verify Database Connection** - Make sure PostgreSQL is linked
3. **Check Environment Variables** - Ensure `DATABASE_URL` is set
4. **Try Different Browser** - Clear cookies/cache
5. **Check Case Sensitivity** - Username/password are case-sensitive

## Debug Mode

The updated login function now prints debug info. Check Render logs when you try to login to see:
- If user is found
- If password check passes/fails
- Account status (active, admin)

