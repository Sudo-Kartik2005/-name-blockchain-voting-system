#!/usr/bin/env python3
"""
Check existing users and create admin if needed
Works on both local and Render
"""
import os
import sys
from app_factory import create_app
from models import Voter, db
from werkzeug.security import generate_password_hash
from datetime import datetime

def check_users():
    """Check all existing users in database"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("CHECKING EXISTING USERS IN DATABASE")
        print("=" * 60)
        
        all_users = Voter.query.all()
        print(f"\nTotal users found: {len(all_users)}")
        
        if all_users:
            print("\n📋 Existing Users:")
            print("-" * 60)
            for user in all_users:
                admin_status = "👑 ADMIN" if user.is_admin else "👤 User"
                print(f"{admin_status} | Username: {user.username} | Email: {user.email} | Active: {user.is_active}")
        else:
            print("\n⚠️  No users found in database!")
        
        admins = Voter.query.filter_by(is_admin=True).all()
        print(f"\n👑 Admin users: {len(admins)}")
        
        if admins:
            print("\nAdmin Credentials:")
            for admin in admins:
                print(f"  - Username: {admin.username} | Email: {admin.email}")
        else:
            print("\n⚠️  No admin users found!")
        
        return len(admins) > 0

def create_admin_interactive():
    """Interactively create admin user"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "=" * 60)
        print("CREATE ADMIN USER")
        print("=" * 60)
        
        # Check if admin exists
        existing_admin = Voter.query.filter_by(username='newadmin').first()
        if existing_admin:
            print("\n⚠️  Admin user 'newadmin' already exists!")
            choice = input("Update it to admin status? (y/n): ").lower()
            if choice == 'y':
                existing_admin.is_admin = True
                existing_admin.password_hash = generate_password_hash('123456')
                existing_admin.is_active = True
                db.session.commit()
                print("\n✅ Admin user 'newadmin' updated!")
                print("   Username: newadmin")
                print("   Password: 123456")
                return
            else:
                print("Skipping update.")
                return
        
        # Create new admin
        print("\nCreating new admin user...")
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
        
        print("\n✅ Admin user created successfully!")
        print("\n📋 Admin Credentials:")
        print("   Username: newadmin")
        print("   Password: 123456")
        print("\n🌐 Login at: https://your-app.onrender.com/login")
        print("\n⚠️  IMPORTANT: Change password after first login!")

def reset_admin_password(username='newadmin', new_password='123456'):
    """Reset admin password"""
    app = create_app()
    
    with app.app_context():
        user = Voter.query.filter_by(username=username).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            user.is_admin = True
            user.is_active = True
            db.session.commit()
            print(f"\n✅ Password reset for '{username}'")
            print(f"   New password: {new_password}")
        else:
            print(f"\n❌ User '{username}' not found!")
            print("Creating new admin user...")
            admin = Voter(
                username=username,
                email=f'{username}@votingsystem.com',
                password_hash=generate_password_hash(new_password),
                first_name='Admin',
                last_name='User',
                date_of_birth=datetime(1990, 1, 1).date(),
                voter_id=f'ADMIN_{username.upper()}',
                is_admin=True,
                is_verified=True,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Admin '{username}' created!")
            print(f"   Password: {new_password}")

if __name__ == "__main__":
    print("\n🔍 Checking database for users...")
    has_admin = check_users()
    
    if not has_admin:
        print("\n" + "=" * 60)
        print("NO ADMIN USER FOUND!")
        print("=" * 60)
        create_admin_interactive()
    else:
        print("\n✅ Admin user exists!")
        print("\nIf you forgot the password, you can reset it.")
        choice = input("\nReset admin password? (y/n): ").lower()
        if choice == 'y':
            reset_admin_password()

