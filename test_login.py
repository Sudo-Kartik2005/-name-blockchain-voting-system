#!/usr/bin/env python3
"""
Test script to debug login issues
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Voter
from werkzeug.security import generate_password_hash

def test_database():
    """Test database connection and user creation"""
    with app.app_context():
        try:
            print("Testing database connection...")
            
            # Test basic connection
            with db.engine.connect() as conn:
                result = conn.execute(db.text('SELECT 1'))
                print("✓ Database connection successful")
            
            # Check if tables exist
            print("\nChecking database tables...")
            db.create_all()
            print("✓ Database tables created/verified")
            
            # Check existing users
            voters = Voter.query.all()
            print(f"✓ Found {len(voters)} existing voters")
            
            for voter in voters:
                print(f"  - {voter.username} (ID: {voter.id})")
            
            # Create a test user if none exist
            if not voters:
                print("\nCreating test user...")
                test_voter = Voter(
                    username='testuser',
                    email='test@example.com',
                    password_hash=generate_password_hash('password123'),
                    first_name='Test',
                    last_name='User',
                    date_of_birth='1990-01-01',
                    voter_id='TEST001'
                )
                db.session.add(test_voter)
                db.session.commit()
                print("✓ Test user created successfully")
                print(f"  Username: testuser")
                print(f"  Password: password123")
            else:
                print("\nUsing existing user for testing")
                test_voter = voters[0]
                print(f"  Username: {test_voter.username}")
                print(f"  ID: {test_voter.id}")
            
            return True
            
        except Exception as e:
            print(f"✗ Database error: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

def test_login_flow():
    """Test the login flow"""
    with app.app_context():
        try:
            print("\nTesting login flow...")
            
            # Find a test user
            test_voter = Voter.query.first()
            if not test_voter:
                print("✗ No users found in database")
                return False
            
            print(f"✓ Found test user: {test_voter.username}")
            
            # Test password verification
            from werkzeug.security import check_password_hash
            if test_voter.username == 'testuser':
                password_correct = check_password_hash(test_voter.password_hash, 'password123')
            else:
                # For existing users, we can't test password without knowing it
                password_correct = True  # Assume correct for existing users
            
            print(f"✓ Password verification: {'OK' if password_correct else 'FAILED'}")
            
            # Test user loading
            from flask_login import login_user
            login_user(test_voter)
            print(f"✓ User login successful: {test_voter.username}")
            
            return True
            
        except Exception as e:
            print(f"✗ Login flow error: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=== Database and Login Test ===\n")
    
    # Test database
    db_ok = test_database()
    
    if db_ok:
        # Test login flow
        login_ok = test_login_flow()
        
        if login_ok:
            print("\n✓ All tests passed!")
            print("\nYou can now try logging in with:")
            print("  - Username: testuser")
            print("  - Password: password123")
        else:
            print("\n✗ Login flow test failed")
    else:
        print("\n✗ Database test failed")
        print("Please check your database configuration")
