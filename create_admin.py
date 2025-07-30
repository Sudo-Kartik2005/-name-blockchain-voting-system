#!/usr/bin/env python3
"""
Create Admin User Script
This script creates a new admin user with a simple password
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Voter
from werkzeug.security import generate_password_hash

def create_new_admin():
    """Create a new admin user"""
    print("🔧 Creating new admin user...")
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = Voter.query.filter_by(username='newadmin').first()
        if existing_admin:
            print("⚠️  Admin user 'newadmin' already exists! Updating credentials and admin status...")
            existing_admin.password_hash = generate_password_hash('123456')
            existing_admin.is_admin = True
            db.session.commit()
            print("✅ Admin user 'newadmin' updated successfully!")
            print("\n📋 Login Credentials:")
            print("   Username: newadmin")
            print("   Password: 123456")
            print("\n🌐 Go to http://localhost:8080 and login with these credentials")
            return
        
        # Create new admin user
        new_admin = Voter(
            username='newadmin',
            email='newadmin@votingsystem.com',
            password_hash=generate_password_hash('123456'),
            first_name='New',
            last_name='Admin',
            date_of_birth=datetime(1990, 1, 1).date(),
            voter_id='ADMIN001',
            is_verified=True,
            is_admin=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        print("✅ New admin user created successfully!")
        print("\n📋 Login Credentials:")
        print("   Username: newadmin")
        print("   Password: 123456")
        print("\n🌐 Go to http://localhost:8080 and login with these credentials")

if __name__ == "__main__":
    create_new_admin() 