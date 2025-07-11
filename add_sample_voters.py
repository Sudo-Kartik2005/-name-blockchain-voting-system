#!/usr/bin/env python3
"""
Add sample voters to the database for testing/demo purposes.
"""

from app import app, db
from models import Voter
from werkzeug.security import generate_password_hash
from datetime import datetime

def add_sample_voters():
    sample_voters = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': datetime(1995, 5, 15),
            'voter_id': 'VOTER001',
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'date_of_birth': datetime(1997, 8, 22),
            'voter_id': 'VOTER002',
        },
        {
            'username': 'alice_wong',
            'email': 'alice@example.com',
            'first_name': 'Alice',
            'last_name': 'Wong',
            'date_of_birth': datetime(1996, 3, 10),
            'voter_id': 'VOTER003',
        },
        {
            'username': 'bob_lee',
            'email': 'bob@example.com',
            'first_name': 'Bob',
            'last_name': 'Lee',
            'date_of_birth': datetime(1998, 12, 5),
            'voter_id': 'VOTER004',
        },
        {
            'username': 'carol_kim',
            'email': 'carol@example.com',
            'first_name': 'Carol',
            'last_name': 'Kim',
            'date_of_birth': datetime(1999, 7, 30),
            'voter_id': 'VOTER005',
        },
    ]
    
    with app.app_context():
        for voter_data in sample_voters:
            # Check if voter already exists
            existing = Voter.query.filter_by(username=voter_data['username']).first()
            if existing:
                print(f"Voter {voter_data['username']} already exists. Skipping.")
                continue
            voter = Voter(
                username=voter_data['username'],
                email=voter_data['email'],
                password_hash=generate_password_hash('password123'),
                first_name=voter_data['first_name'],
                last_name=voter_data['last_name'],
                date_of_birth=voter_data['date_of_birth'],
                voter_id=voter_data['voter_id'],
                is_verified=True
            )
            db.session.add(voter)
            print(f"Added voter: {voter.username}")
        db.session.commit()
        print("✅ Sample voters added successfully!")

if __name__ == "__main__":
    add_sample_voters() 