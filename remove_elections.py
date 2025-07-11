#!/usr/bin/env python3
"""
Remove all active elections from the database
"""

from app import app, db
from models import Election, Candidate, Vote

def remove_all_elections():
    """Remove all elections and their associated data"""
    print("🗑️  Removing all elections...")
    print("=" * 50)
    
    with app.app_context():
        # Get all elections
        elections = Election.query.all()
        
        if not elections:
            print("❌ No elections found in the database.")
            return
        
        print(f"📋 Found {len(elections)} election(s):")
        for election in elections:
            print(f"  - {election.title} (ID: {election.id})")
            print(f"    Start: {election.start_date.strftime('%Y-%m-%d')}")
            print(f"    End: {election.end_date.strftime('%Y-%m-%d')}")
            print(f"    Active: {election.is_active}")
            print()
        
        # Count associated data
        total_candidates = Candidate.query.count()
        total_votes = Vote.query.count()
        
        print(f"📊 Associated data:")
        print(f"  - Candidates: {total_candidates}")
        print(f"  - Votes: {total_votes}")
        print()
        
        # Confirm deletion
        confirm = input("⚠️  Are you sure you want to delete ALL elections? This will also delete all candidates and votes. (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Operation cancelled.")
            return
        
        # Delete all votes first (due to foreign key constraints)
        print("🗑️  Deleting votes...")
        Vote.query.delete()
        
        # Delete all candidates
        print("🗑️  Deleting candidates...")
        Candidate.query.delete()
        
        # Delete all elections
        print("🗑️  Deleting elections...")
        Election.query.delete()
        
        # Commit changes
        db.session.commit()
        
        print("✅ All elections have been removed successfully!")
        print(f"   - Deleted {len(elections)} election(s)")
        print(f"   - Deleted {total_candidates} candidate(s)")
        print(f"   - Deleted {total_votes} vote(s)")

if __name__ == "__main__":
    remove_all_elections() 