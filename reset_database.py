#!/usr/bin/env python3
"""
Reset Database Script for Blockchain Voting System
This script drops all tables and recreates them
"""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, init_db
from models import Voter, Election, Candidate, BlockchainState
from werkzeug.security import generate_password_hash

def reset_database():
    """Drop all tables and recreate them"""
    print("🔄 Resetting database...")
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("✅ All tables dropped")
        
        # Recreate all tables
        db.create_all()
        print("✅ All tables recreated")
        
        # Create initial blockchain state
        blockchain_state = BlockchainState()
        db.session.add(blockchain_state)
        db.session.commit()
        print("✅ Initial blockchain state created")

def create_sample_data():
    """Create sample data for testing"""
    print("📝 Creating sample data...")
    
    with app.app_context():
        # Create sample voters
        voters_data = [
            {
                'username': 'admin',
                'email': 'admin@votingsystem.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'User',
                'date_of_birth': datetime(1990, 1, 1).date(),
                'voter_id': 'VOTER001'
            },
            {
                'username': 'voter1',
                'email': 'voter1@example.com',
                'password': 'password123',
                'first_name': 'John',
                'last_name': 'Doe',
                'date_of_birth': datetime(1985, 5, 15).date(),
                'voter_id': 'VOTER002'
            },
            {
                'username': 'voter2',
                'email': 'voter2@example.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'date_of_birth': datetime(1992, 8, 22).date(),
                'voter_id': 'VOTER003'
            }
        ]
        
        for voter_data in voters_data:
            voter = Voter(
                username=voter_data['username'],
                email=voter_data['email'],
                password_hash=generate_password_hash(voter_data['password']),
                first_name=voter_data['first_name'],
                last_name=voter_data['last_name'],
                date_of_birth=voter_data['date_of_birth'],
                voter_id=voter_data['voter_id'],
                is_verified=True
            )
            db.session.add(voter)
        
        # Create sample elections
        elections_data = [
            {
                'title': 'Student Council Election 2024',
                'description': 'Annual election for student council positions',
                'start_date': datetime.now() - timedelta(days=1),
                'end_date': datetime.now() + timedelta(days=7)
            },
            {
                'title': 'Class Representative Election',
                'description': 'Election for class representative position',
                'start_date': datetime.now() + timedelta(days=1),
                'end_date': datetime.now() + timedelta(days=14)
            }
        ]
        
        for election_data in elections_data:
            election = Election(**election_data)
            db.session.add(election)
        
        db.session.commit()
        
        # Create sample candidates
        candidates_data = [
            {
                'name': 'Alice Johnson',
                'party': 'Progressive Party',
                'description': 'Experienced student leader with focus on inclusivity',
                'election_id': Election.query.filter_by(title='Student Council Election 2024').first().id
            },
            {
                'name': 'Bob Wilson',
                'party': 'Conservative Party',
                'description': 'Advocate for traditional values and fiscal responsibility',
                'election_id': Election.query.filter_by(title='Student Council Election 2024').first().id
            },
            {
                'name': 'Carol Davis',
                'party': 'Independent',
                'description': 'Independent candidate focused on student welfare',
                'election_id': Election.query.filter_by(title='Student Council Election 2024').first().id
            },
            {
                'name': 'David Brown',
                'party': 'Liberal Party',
                'description': 'Progressive policies for modern education',
                'election_id': Election.query.filter_by(title='Class Representative Election').first().id
            },
            {
                'name': 'Eva Garcia',
                'party': 'Green Party',
                'description': 'Environmental advocate and community organizer',
                'election_id': Election.query.filter_by(title='Class Representative Election').first().id
            }
        ]
        
        for candidate_data in candidates_data:
            candidate = Candidate(**candidate_data)
            db.session.add(candidate)
        
        db.session.commit()
        print("✅ Sample data created successfully!")

def main():
    """Main function to reset and initialize the database"""
    print("🚀 Blockchain Voting System - Database Reset\n")
    
    try:
        # Reset the database
        reset_database()
        
        # Create sample data
        create_sample_data()
        
        print("\n🎉 Database reset completed successfully!")
        print("\n📋 Database Information:")
        print(f"   Database file: {os.path.abspath('instance/voting_system.db')}")
        print(f"   Tables created: Voter, Election, Candidate, Vote, BlockchainState, PendingTransaction")
        
        print("\n👥 Sample Users Created:")
        print("   Admin: username='admin', password='admin123'")
        print("   Voter1: username='voter1', password='password123'")
        print("   Voter2: username='voter2', password='password123'")
        
        print("\n🗳️ Sample Elections Created:")
        print("   - Student Council Election 2024 (Active)")
        print("   - Class Representative Election (Upcoming)")
        
        print("\n📋 Next Steps:")
        print("   1. Start the application: python app.py")
        print("   2. Visit: http://localhost:8080")
        print("   3. Login with admin credentials to manage elections")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 