#!/usr/bin/env python3
"""
Check Users Script
This script shows all users in the database
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Voter

def check_users():
    """Check all users in the database"""
    print("👥 Checking users in database...")
    
    with app.app_context():
        users = Voter.query.all()
        
        if not users:
            print("❌ No users found in database!")
            return
        
        print(f"✅ Found {len(users)} users:")
        print("\n📋 User List:")
        for user in users:
            print(f"   - Username: {user.username}")
            print(f"     Email: {user.email}")
            print(f"     Voter ID: {user.voter_id}")
            print(f"     Verified: {user.is_verified}")
            print(f"     Active: {user.is_active}")
            print()

if __name__ == "__main__":
    check_users() 