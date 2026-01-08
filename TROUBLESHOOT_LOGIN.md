# 🔧 Troubleshooting Login Issues

## Problem: "Invalid username or password"

This usually means:
1. **Admin user doesn't exist** in the database
2. **Wrong credentials** are being used
3. **Password hash mismatch** (rare)

## Quick Fix: Create Admin User on Render

### Step 1: Access Render Shell

1. Go to **Render Dashboard**
2. Open your **Web Service**
3. Click **"Shell"** tab (or "Console")

### Step 2: Check Existing Users

Run this to see all users:
```python
from app_factory import create_app
from models import Voter

app = create_app()
with app.app_context():
    users = Voter.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        admin = "ADMIN" if user.is_admin else "USER"
        print(f"{admin}: {user.username} ({user.email})")
```

### Step 3: Create Admin User

**Option A: Use the script**
```bash
python create_admin.py
```

**Option B: Manual creation (Python)**
```python
from app_factory import create_app
from models import Voter, db
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()
with app.app_context():
    # Check if user exists
    user = Voter.query.filter_by(username='newadmin').first()
    if user:
        # Update existing user to admin
        user.is_admin = True
        user.password_hash = generate_password_hash('123456')
        user.is_active = True
        db.session.commit()
        print("✅ Updated existing user to admin")
    else:
        # Create new admin
        admin = Voter(
            username='newadmin',
            email='admin@votingsystem.com',
            password_hash=generate_password_hash('123456'),
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
        print("✅ Admin created!")
    
    print("\n📋 Login Credentials:")
    print("   Username: newadmin")
    print("   Password: 123456")
```

### Step 4: Verify Admin Was Created

```python
from app_factory import create_app
from models import Voter

app = create_app()
with app.app_context():
    admin = Voter.query.filter_by(username='newadmin', is_admin=True).first()
    if admin:
        print("✅ Admin found!")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Is Admin: {admin.is_admin}")
        print(f"   Is Active: {admin.is_active}")
    else:
        print("❌ Admin not found!")
```

## Default Admin Credentials

After running `create_admin.py`:
- **Username**: `newadmin`
- **Password**: `123456`

## Common Issues

### Issue 1: User exists but password doesn't work

**Solution**: Reset the password:
```python
from app_factory import create_app
from models import Voter, db
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    user = Voter.query.filter_by(username='newadmin').first()
    if user:
        user.password_hash = generate_password_hash('123456')
        user.is_active = True
        db.session.commit()
        print("✅ Password reset!")
```

### Issue 2: User exists but is_admin is False

**Solution**: Make them admin:
```python
from app_factory import create_app
from models import Voter, db

app = create_app()
with app.app_context():
    user = Voter.query.filter_by(username='newadmin').first()
    if user:
        user.is_admin = True
        user.is_active = True
        db.session.commit()
        print("✅ User is now admin!")
```

### Issue 3: User exists but is_active is False

**Solution**: Activate the account:
```python
from app_factory import create_app
from models import Voter, db

app = create_app()
with app.app_context():
    user = Voter.query.filter_by(username='newadmin').first()
    if user:
        user.is_active = True
        db.session.commit()
        print("✅ Account activated!")
```

## Complete Admin Setup (All-in-One)

Run this complete setup:
```python
from app_factory import create_app
from models import Voter, db
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()
with app.app_context():
    username = 'newadmin'
    password = '123456'
    
    user = Voter.query.filter_by(username=username).first()
    if user:
        # Update existing user
        user.password_hash = generate_password_hash(password)
        user.is_admin = True
        user.is_active = True
        user.is_verified = True
        print(f"✅ Updated '{username}' to admin")
    else:
        # Create new admin
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
        print(f"✅ Created admin '{username}'")
    
    db.session.commit()
    
    # Verify
    admin = Voter.query.filter_by(username=username).first()
    print(f"\n✅ Verification:")
    print(f"   Username: {admin.username}")
    print(f"   Is Admin: {admin.is_admin}")
    print(f"   Is Active: {admin.is_active}")
    print(f"\n📋 Login with:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
```

## Test Login

After creating admin, test it:
1. Go to: `https://your-app.onrender.com/login`
2. Enter:
   - Username: `newadmin`
   - Password: `123456`
3. Click Login

If it still fails, check Render logs for errors.

