# 🔐 Admin Credentials Guide

## Current Admin Users

There are **no admin users created by default** on Render. You need to create one manually.

## Default Admin Credentials (if created via script)

If you run `create_admin.py`, it creates:
- **Username**: `newadmin`
- **Password**: `123456`

**Note**: These are default/development credentials. Change immediately after first login!

## How to Create Admin on Render

### Method 1: Using Render Shell (Easiest)

1. **Go to Render Dashboard**
   - Open your **Web Service**
   - Click on **"Shell"** tab (or "Console")

2. **Run Admin Creation Script:**
   ```bash
   python create_admin.py
   ```

3. **Or Run Python Interactively:**
   ```python
   from app_factory import create_app
   from models import Voter, db
   from werkzeug.security import generate_password_hash
   from datetime import datetime
   
   app = create_app()
   with app.app_context():
       # Create admin
       admin = Voter(
           username='admin',
           email='admin@example.com',
           password_hash=generate_password_hash('admin123'),
           first_name='Admin',
           last_name='User',
           date_of_birth=datetime(1990, 1, 1).date(),
           voter_id='ADMIN001',
           is_admin=True,
           is_verified=True
       )
       db.session.add(admin)
       db.session.commit()
       print("✅ Admin created!")
       print("Username: admin")
       print("Password: admin123")
   ```

### Method 2: Make Existing User an Admin

If you already registered a regular user, you can make them admin:

```python
from app_factory import create_app
from models import Voter, db

app = create_app()
with app.app_context():
    # Replace 'YOUR_USERNAME' with your actual username
    user = Voter.query.filter_by(username='YOUR_USERNAME').first()
    if user:
        user.is_admin = True
        db.session.commit()
        print(f"✅ {user.username} is now an admin!")
    else:
        print("❌ User not found")
```

## Admin Credentials Reference

| Script/Scenario | Username | Password | Notes |
|----------------|----------|----------|-------|
| `create_admin.py` | `newadmin` | `123456` | Default script |
| `create_database.py` | `admin` | `admin123` | Sample data script |
| Manual creation | Your choice | Your choice | Custom credentials |

## Security Recommendations

1. **Change default password immediately**
2. **Use strong passwords** (min 12 characters, mixed case, numbers, symbols)
3. **Don't share admin credentials**
4. **Use unique voter_id** for admin accounts
5. **Consider creating multiple admin accounts** for backup

## Check Existing Admins

To see all admin users:

```python
from app_factory import create_app
from models import Voter

app = create_app()
with app.app_context():
    admins = Voter.query.filter_by(is_admin=True).all()
    for admin in admins:
        print(f"Admin: {admin.username} ({admin.email})")
```

Or run:
```bash
python list_admins.py
```

## Quick Admin Creation Commands

**Create admin via script:**
```bash
python create_admin.py
```
Creates: `newadmin` / `123456`

**Create custom admin (interactive Python):**
```python
# See Method 1 above for full code
# Creates: admin / admin123 (or customize)
```

**Promote existing user:**
```python
# See Method 2 above
# Uses existing user credentials
```

