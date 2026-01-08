#!/usr/bin/env python3
"""
Test login credentials and verify users in database
"""
from app_factory import create_app
from models import Voter, db
from werkzeug.security import check_password_hash, generate_password_hash

def test_login(username, password):
    """Test if login credentials work"""
    app = create_app()
    
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"Testing Login for: {username}")
        print(f"{'='*60}")
        
        # Find user
        voter = Voter.query.filter_by(username=username).first()
        
        if not voter:
            print(f"❌ User '{username}' NOT FOUND in database!")
            return False
        
        print(f"✅ User found:")
        print(f"   Username: {voter.username}")
        print(f"   Email: {voter.email}")
        print(f"   Is Admin: {voter.is_admin}")
        print(f"   Is Active: {voter.is_active}")
        print(f"   Is Verified: {voter.is_verified}")
        
        # Test password
        if check_password_hash(voter.password_hash, password):
            print(f"✅ Password is CORRECT!")
            return True
        else:
            print(f"❌ Password is INCORRECT!")
            print(f"   Password hash stored: {voter.password_hash[:50]}...")
            return False

def list_all_users():
    """List all users in database"""
    app = create_app()
    
    with app.app_context():
        users = Voter.query.all()
        print(f"\n{'='*60}")
        print(f"ALL USERS IN DATABASE ({len(users)} total)")
        print(f"{'='*60}")
        
        if not users:
            print("❌ No users found in database!")
            return
        
        for user in users:
            admin = "👑 ADMIN" if user.is_admin else "👤 USER"
            active = "✅ Active" if user.is_active else "❌ Inactive"
            print(f"\n{admin} | {active}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Voter ID: {user.voter_id}")
            print(f"   Created: {user.created_at}")

def create_admin_secure():
    """Create admin with secure password"""
    app = create_app()
    
    with app.app_context():
        username = 'newadmin'
        password = '123456'
        
        print(f"\n{'='*60}")
        print("CREATING ADMIN USER")
        print(f"{'='*60}")
        
        # Check if exists
        existing = Voter.query.filter_by(username=username).first()
        if existing:
            print(f"⚠️  User '{username}' already exists. Updating...")
            existing.is_admin = True
            existing.is_active = True
            existing.password_hash = generate_password_hash(password)
            db.session.commit()
            print(f"✅ Updated '{username}' to admin")
        else:
            from datetime import datetime
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
        admin = Voter.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            print(f"\n✅ VERIFICATION SUCCESSFUL!")
            print(f"\n📋 Login Credentials:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"\n🌐 Login at: https://your-app.onrender.com/login")
            return True
        else:
            print(f"\n❌ VERIFICATION FAILED!")
            return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_all_users()
        elif sys.argv[1] == "create":
            create_admin_secure()
        elif sys.argv[1] == "test" and len(sys.argv) >= 4:
            test_login(sys.argv[2], sys.argv[3])
        else:
            print("Usage:")
            print("  python test_login.py list          - List all users")
            print("  python test_login.py create        - Create admin user")
            print("  python test_login.py test USER PASS - Test login")
    else:
        # Default: list users and create admin if needed
        list_all_users()
        admins = Voter.query.filter_by(is_admin=True).all()
        if not admins:
            print("\n⚠️  No admin found! Creating one...")
            create_admin_secure()
        else:
            print(f"\n✅ Found {len(admins)} admin user(s)")
            # Test admin login
            test_login('newadmin', '123456')

