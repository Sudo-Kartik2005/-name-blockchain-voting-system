#!/usr/bin/env python3
"""
Debug script to test login step by step
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Voter
from werkzeug.security import check_password_hash

def test_user_loading():
    """Test if users can be loaded from database"""
    with app.app_context():
        try:
            print("=== Testing User Loading ===")
            
            # Get all users
            voters = Voter.query.all()
            print(f"Found {len(voters)} users in database")
            
            # Test specific user
            admin_user = Voter.query.filter_by(username='admin').first()
            if admin_user:
                print(f"✓ Admin user found: {admin_user.username}")
                print(f"  ID: {admin_user.id}")
                print(f"  Email: {admin_user.email}")
                print(f"  Is admin: {admin_user.is_admin}")
                
                # Test password (we'll use a common password)
                test_passwords = ['admin', 'password', '123456', 'admin123']
                password_found = False
                
                for test_pwd in test_passwords:
                    if check_password_hash(admin_user.password_hash, test_pwd):
                        print(f"✓ Password found: {test_pwd}")
                        password_found = True
                        break
                
                if not password_found:
                    print("✗ Could not verify password (try common passwords)")
                    print("  Try: admin, password, 123456, admin123")
                
                return admin_user
            else:
                print("✗ Admin user not found")
                return None
                
        except Exception as e:
            print(f"✗ Error testing user loading: {e}")
            return None

def test_session_config():
    """Test session configuration"""
    print("\n=== Testing Session Configuration ===")
    
    print(f"SECRET_KEY: {app.config.get('SECRET_KEY', 'NOT SET')[:20]}...")
    print(f"SESSION_COOKIE_SECURE: {app.config.get('SESSION_COOKIE_SECURE')}")
    print(f"SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
    print(f"SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")
    print(f"PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')}")

def test_flask_login_config():
    """Test Flask-Login configuration"""
    print("\n=== Testing Flask-Login Configuration ===")
    
    print(f"Login view: {app.config.get('LOGIN_VIEW', 'NOT SET')}")
    print(f"Login manager initialized: {'login_manager' in dir(app)}")
    
    # Check if login_manager is properly configured
    if hasattr(app, 'login_manager'):
        print(f"✓ Login manager found")
        print(f"  Login view: {app.login_manager.login_view}")
        print(f"  User loader: {app.login_manager.user_loader}")
    else:
        print("✗ Login manager not found")

if __name__ == '__main__':
    print("=== Login Debug Script ===\n")
    
    # Test session config
    test_session_config()
    
    # Test Flask-Login config
    test_flask_login_config()
    
    # Test user loading
    user = test_user_loading()
    
    if user:
        print(f"\n✓ User loading successful")
        print(f"  You can try logging in with username: {user.username}")
        print(f"  Common passwords to try: admin, password, 123456, admin123")
    else:
        print("\n✗ User loading failed")
    
    print("\n=== Debug Complete ===")
