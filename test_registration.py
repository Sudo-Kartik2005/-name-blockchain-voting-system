#!/usr/bin/env python3
"""
Test script for registration functionality
"""

import os
import sys
from app import app, db
from models import Voter
from forms import RegistrationForm
from datetime import date

def test_registration_form():
    """Test registration form validation"""
    print("=== Testing Registration Form ===")
    
    with app.app_context():
        # Test valid data
        form_data = {
            'username': 'testuser123',
            'email': 'test@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': date(1990, 1, 1),
            'voter_id': 'VOTER123456'
        }
        
        form = RegistrationForm(data=form_data)
        if form.validate():
            print("✓ Registration form validation passed")
        else:
            print("✗ Registration form validation failed:")
            for field, errors in form.errors.items():
                print(f"  {field}: {errors}")
            return False
    
    return True

def test_voter_creation():
    """Test voter creation in database"""
    print("\n=== Testing Voter Creation ===")
    
    try:
        with app.app_context():
            # Create a test voter
            test_voter = Voter(
                username='testuser456',
                email='test456@example.com',
                password_hash='test_hash',
                first_name='Test',
                last_name='User',
                date_of_birth=date(1990, 1, 1),
                voter_id='VOTER789012'
            )
            
            db.session.add(test_voter)
            db.session.commit()
            print("✓ Voter creation successful")
            
            # Verify voter was created
            created_voter = Voter.query.filter_by(username='testuser456').first()
            if created_voter:
                print(f"✓ Voter found in database: {created_voter.username}")
                
                # Clean up
                db.session.delete(created_voter)
                db.session.commit()
                print("✓ Test voter cleaned up")
            else:
                print("✗ Voter not found in database")
                return False
                
    except Exception as e:
        print(f"✗ Voter creation failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and basic operations"""
    print("\n=== Testing Database Connection ===")
    
    try:
        with app.app_context():
            # Test basic query
            voter_count = Voter.query.count()
            print(f"✓ Current voter count: {voter_count}")
            
            # Test database URL
            print(f"✓ Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting registration tests...")
    
    success = True
    
    # Test database connection
    if not test_database_connection():
        success = False
    
    # Test registration form
    if not test_registration_form():
        success = False
    
    # Test voter creation
    if not test_voter_creation():
        success = False
    
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1) 