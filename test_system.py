#!/usr/bin/env python3
"""
Test script for the Blockchain Voting System
This script tests the core functionality of the voting system
"""

import sys
import time
from datetime import datetime, timedelta
from blockchain import Blockchain
from models import db, Voter, Election, Candidate, Vote, BlockchainState, PendingTransaction
from app import app, init_db
from werkzeug.security import generate_password_hash
import json

def test_blockchain():
    """Test the blockchain functionality"""
    print("🧪 Testing Blockchain Core...")
    
    # Create a new blockchain
    blockchain = Blockchain()
    
    # Test genesis block
    assert len(blockchain.chain) == 1, "Genesis block should be created"
    assert blockchain.chain[0].index == 0, "Genesis block should have index 0"
    assert blockchain.chain[0].previous_hash == "0", "Genesis block should have previous_hash '0'"
    
    # Test adding transactions
    blockchain.add_transaction("voter1", "ELECTION_SYSTEM", {
        "type": "vote",
        "election_id": "test_election",
        "candidate": "Candidate A",
        "voter_id": "voter1"
    })
    
    blockchain.add_transaction("voter2", "ELECTION_SYSTEM", {
        "type": "vote",
        "election_id": "test_election",
        "candidate": "Candidate B",
        "voter_id": "voter2"
    })
    
    # Test mining
    blockchain.mine_pending_transactions("test_miner")
    
    # Verify chain integrity
    assert blockchain.is_chain_valid(), "Blockchain should be valid after mining"
    assert len(blockchain.chain) == 2, "Should have 2 blocks after mining"
    
    # Test vote counting
    results = blockchain.get_election_results("test_election")
    assert results["total_votes"] == 2, "Should have 2 total votes"
    assert results["vote_counts"]["Candidate A"] == 1, "Candidate A should have 1 vote"
    assert results["vote_counts"]["Candidate B"] == 1, "Candidate B should have 1 vote"
    
    print("✅ Blockchain tests passed!")

def test_database():
    """Test the database models"""
    print("🧪 Testing Database Models...")
    
    with app.app_context():
        # Create test voter
        voter = Voter(
            username="testuser",
            email="test@example.com",
            password_hash=generate_password_hash("password123"),
            first_name="Test",
            last_name="User",
            date_of_birth=datetime(1990, 1, 1).date(),
            voter_id="TEST123456"
        )
        db.session.add(voter)
        db.session.commit()
        
        # Create test election
        election = Election(
            title="Test Election",
            description="A test election for testing purposes",
            start_date=datetime.now() - timedelta(hours=1),  # Start 1 hour ago
            end_date=datetime.now() + timedelta(days=7)
        )
        db.session.add(election)
        db.session.commit()
        
        # Create test candidates
        candidate1 = Candidate(
            name="Candidate A",
            party="Party A",
            description="First candidate",
            election_id=election.id
        )
        candidate2 = Candidate(
            name="Candidate B",
            party="Party B",
            description="Second candidate",
            election_id=election.id
        )
        db.session.add_all([candidate1, candidate2])
        db.session.commit()
        
        # Test relationships
        assert len(election.candidates) == 2, "Election should have 2 candidates"
        assert election.is_open, "Election should be open"
        
        print("✅ Database tests passed!")

def test_voting_process():
    """Test the complete voting process"""
    print("🧪 Testing Voting Process...")
    
    with app.app_context():
        # Get test data
        voter = Voter.query.filter_by(username="testuser").first()
        election = Election.query.filter_by(title="Test Election").first()
        candidate = Candidate.query.filter_by(name="Candidate A").first()
        
        # Create a vote
        vote = Vote(
            voter_id=voter.id,
            election_id=election.id,
            candidate_id=candidate.id,
            transaction_hash="test_hash_123"
        )
        db.session.add(vote)
        db.session.commit()
        
        # Verify vote was created
        assert Vote.query.filter_by(voter_id=voter.id, election_id=election.id).first() is not None, "Vote should be created"
        
        print("✅ Voting process tests passed!")

def test_blockchain_integration():
    """Test blockchain integration with database"""
    print("🧪 Testing Blockchain Integration...")
    
    with app.app_context():
        # Create pending transaction
        pending_tx = PendingTransaction(
            transaction_type="vote",
            sender="test_voter",
            recipient="ELECTION_SYSTEM",
            data=json.dumps({
                "type": "vote",
                "election_id": "test_election_2",
                "candidate": "Candidate C",
                "voter_id": "test_voter"
            }),
            timestamp=time.time()
        )
        db.session.add(pending_tx)
        db.session.commit()
        
        # Verify pending transaction
        assert PendingTransaction.query.count() > 0, "Should have pending transactions"
        
        print("✅ Blockchain integration tests passed!")

def run_demo():
    """Run a complete demo of the voting system"""
    print("🎬 Running Complete Demo...")
    
    with app.app_context():
        # Create demo election
        demo_election = Election(
            title="Demo Election 2024",
            description="A demonstration election to showcase the blockchain voting system",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30)
        )
        db.session.add(demo_election)
        db.session.commit()
        
        # Add demo candidates
        candidates = [
            Candidate(name="Alice Johnson", party="Progressive Party", description="Experienced leader with focus on innovation", election_id=demo_election.id),
            Candidate(name="Bob Smith", party="Conservative Party", description="Traditional values with modern solutions", election_id=demo_election.id),
            Candidate(name="Carol Davis", party="Independent", description="Bridging divides for common good", election_id=demo_election.id)
        ]
        db.session.add_all(candidates)
        db.session.commit()
        
        # Create demo voters
        demo_voters = [
            Voter(username="voter1", email="voter1@demo.com", password_hash=generate_password_hash("demo123"),
                  first_name="John", last_name="Doe", date_of_birth=datetime(1985, 5, 15).date(), voter_id="DEMO001"),
            Voter(username="voter2", email="voter2@demo.com", password_hash=generate_password_hash("demo123"),
                  first_name="Jane", last_name="Smith", date_of_birth=datetime(1990, 8, 22).date(), voter_id="DEMO002"),
            Voter(username="voter3", email="voter3@demo.com", password_hash=generate_password_hash("demo123"),
                  first_name="Mike", last_name="Johnson", date_of_birth=datetime(1988, 3, 10).date(), voter_id="DEMO003")
        ]
        db.session.add_all(demo_voters)
        db.session.commit()
        
        print(f"✅ Demo setup complete!")
        print(f"   - Election: {demo_election.title}")
        print(f"   - Candidates: {len(candidates)}")
        print(f"   - Voters: {len(demo_voters)}")
        print(f"   - Election ID: {demo_election.id}")

def main():
    """Run all tests"""
    print("🚀 Starting Blockchain Voting System Tests...\n")
    
    try:
        # Initialize database
        init_db()
        
        # Run tests
        test_blockchain()
        test_database()
        test_voting_process()
        test_blockchain_integration()
        run_demo()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 System Status:")
        print("   ✅ Blockchain core functionality")
        print("   ✅ Database models and relationships")
        print("   ✅ Voting process")
        print("   ✅ Blockchain integration")
        print("   ✅ Demo data created")
        
        print("\n🌐 To start the web application:")
        print("   python app.py")
        print("   Then visit: http://localhost:5000")
        
        print("\n👥 Demo Credentials:")
        print("   Username: voter1, voter2, voter3")
        print("   Password: demo123")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 