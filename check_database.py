#!/usr/bin/env python3
"""
Database check script for debugging database issues on Render
"""

import os
import sys
from app import app, db, init_db
from models import Voter, Election, Candidate, Vote, BlockchainState, PendingTransaction

def check_database():
    """Check database connection and tables"""
    print("=== Database Check Script ===")
    
    try:
        with app.app_context():
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Test database connection
            print("\n1. Testing database connection...")
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            print("✓ Database connection successful")
            
            # Check if tables exist
            print("\n2. Checking tables...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"Found tables: {tables}")
            
            # Check table counts
            print("\n3. Checking table counts...")
            try:
                voter_count = Voter.query.count()
                print(f"Voters: {voter_count}")
            except Exception as e:
                print(f"Error counting voters: {e}")
            
            try:
                election_count = Election.query.count()
                print(f"Elections: {election_count}")
            except Exception as e:
                print(f"Error counting elections: {e}")
            
            try:
                candidate_count = Candidate.query.count()
                print(f"Candidates: {candidate_count}")
            except Exception as e:
                print(f"Error counting candidates: {e}")
            
            try:
                vote_count = Vote.query.count()
                print(f"Votes: {vote_count}")
            except Exception as e:
                print(f"Error counting votes: {e}")
            
            try:
                blockchain_state_count = BlockchainState.query.count()
                print(f"Blockchain States: {blockchain_state_count}")
            except Exception as e:
                print(f"Error counting blockchain states: {e}")
            
            try:
                pending_tx_count = PendingTransaction.query.count()
                print(f"Pending Transactions: {pending_tx_count}")
            except Exception as e:
                print(f"Error counting pending transactions: {e}")
            
            print("\n✓ Database check completed successfully")
            
    except Exception as e:
        print(f"\n✗ Database check failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    
    return True

def initialize_database():
    """Initialize database tables"""
    print("\n=== Initializing Database ===")
    try:
        init_db()
        print("✓ Database initialization completed")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        success = initialize_database()
    else:
        success = check_database()
    
    if not success:
        sys.exit(1) 