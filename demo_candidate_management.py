#!/usr/bin/env python3
"""
Demonstration script for candidate management functionality
This script shows how to use the new candidate editing and deletion features.
"""

from app import app, db
from models import Election, Candidate, Voter

def demo_candidate_management():
    """Demonstrate the candidate management features"""
    
    with app.app_context():
        print("🎯 Candidate Management System Demo")
        print("=" * 50)
        
        # Get the first election for demonstration
        election = Election.query.first()
        if not election:
            print("❌ No elections found. Please create an election first.")
            return
        
        print(f"📋 Election: {election.title}")
        print(f"📅 Period: {election.start_date.strftime('%Y-%m-%d')} to {election.end_date.strftime('%Y-%m-%d')}")
        
        # Show current candidates
        candidates = Candidate.query.filter_by(election_id=election.id).all()
        print(f"\n👥 Current Candidates ({len(candidates)}):")
        for i, candidate in enumerate(candidates, 1):
            print(f"  {i}. {candidate.name}")
            if candidate.party:
                print(f"     Party: {candidate.party}")
            if candidate.description:
                print(f"     Description: {candidate.description}")
            print()
        
        if candidates:
            # Demonstrate editing the first candidate
            candidate = candidates[0]
            print(f"✏️  Editing candidate: {candidate.name}")
            
            # Show current data
            print(f"   Current name: {candidate.name}")
            print(f"   Current party: {candidate.party or 'None'}")
            print(f"   Current description: {candidate.description or 'None'}")
            
            # Simulate updating the candidate
            old_name = candidate.name
            candidate.name = f"{candidate.name} (Updated)"
            candidate.party = candidate.party or "Independent"
            candidate.description = candidate.description or "Updated description"
            
            print(f"\n   New name: {candidate.name}")
            print(f"   New party: {candidate.party}")
            print(f"   New description: {candidate.description}")
            
            # Revert the change for demo purposes
            candidate.name = old_name
            db.session.commit()
            
            print("   ✅ Candidate updated successfully!")
        
        print("\n🔧 Available Actions:")
        print("   1. Edit candidate details (name, party, description)")
        print("   2. Delete candidates (only if no votes cast)")
        print("   3. Add new candidates")
        print("   4. View all candidates for an election")
        
        print("\n🌐 Web Interface:")
        print(f"   - Manage candidates: /admin/election/{election.id}/candidates")
        print(f"   - Edit candidate: /admin/election/{election.id}/candidate/<candidate_id>/edit")
        print(f"   - Delete candidate: POST to /admin/election/{election.id}/candidate/<candidate_id>/delete")
        
        print("\n✅ Candidate management system is ready!")

if __name__ == "__main__":
    demo_candidate_management() 