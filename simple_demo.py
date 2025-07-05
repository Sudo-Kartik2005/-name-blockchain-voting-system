#!/usr/bin/env python3
"""
Simplified Blockchain Voting System Demo
This demo works without external dependencies to showcase the core functionality
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

class SimpleBlock:
    """Simplified Block class for demonstration"""
    def __init__(self, index: int, transactions: List[Dict], timestamp: float, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        """Mine the block with the specified difficulty"""
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class SimpleBlockchain:
    """Simplified Blockchain class for demonstration"""
    def __init__(self):
        self.chain: List[SimpleBlock] = []
        self.difficulty = 2  # Lower difficulty for demo
        self.pending_transactions: List[Dict] = []
        
        # Create the genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = SimpleBlock(0, [], time.time(), "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print(f"✅ Genesis block created: {genesis_block.hash[:10]}...")
    
    def add_transaction(self, sender: str, recipient: str, data: Dict) -> None:
        """Add a new transaction to pending transactions"""
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'data': data,
            'timestamp': time.time(),
            'transaction_id': str(uuid.uuid4())
        }
        self.pending_transactions.append(transaction)
        print(f"📝 Transaction added: {sender} -> {recipient}")
    
    def mine_pending_transactions(self, miner_address: str) -> None:
        """Mine all pending transactions and add them to the blockchain"""
        if not self.pending_transactions:
            print("ℹ️  No pending transactions to mine")
            return
        
        print(f"⛏️  Mining {len(self.pending_transactions)} transactions...")
        
        # Create a new block with all pending transactions
        block = SimpleBlock(
            len(self.chain),
            self.pending_transactions,
            time.time(),
            self.chain[-1].hash
        )
        
        # Mine the block
        block.mine_block(self.difficulty)
        
        # Add the block to the chain
        self.chain.append(block)
        
        print(f"✅ Block {block.index} mined: {block.hash[:10]}...")
        print(f"   Nonce: {block.nonce}")
        print(f"   Transactions: {len(self.pending_transactions)}")
        
        # Reset pending transactions
        self.pending_transactions = []
    
    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_election_results(self, election_id: str) -> Dict[str, Any]:
        """Get detailed results for a specific election"""
        votes = []
        vote_counts = {}
        
        for block in self.chain:
            for transaction in block.transactions:
                if (transaction['data'].get('type') == 'vote' and 
                    transaction['data'].get('election_id') == election_id):
                    vote_data = transaction['data']
                    votes.append({
                        'voter_id': transaction['sender'],
                        'candidate': vote_data.get('candidate'),
                        'timestamp': transaction['timestamp'],
                        'block_index': block.index
                    })
                    
                    candidate = vote_data.get('candidate')
                    if candidate:
                        vote_counts[candidate] = vote_counts.get(candidate, 0) + 1
        
        return {
            'election_id': election_id,
            'total_votes': len(votes),
            'vote_counts': vote_counts,
            'votes': votes
        }
    
    def display_chain(self) -> None:
        """Display the blockchain"""
        print(f"\n🔗 Blockchain Status:")
        print(f"   Total blocks: {len(self.chain)}")
        print(f"   Pending transactions: {len(self.pending_transactions)}")
        print(f"   Chain valid: {self.is_chain_valid()}")
        
        for i, block in enumerate(self.chain):
            print(f"\n   Block {i}:")
            print(f"     Hash: {block.hash[:20]}...")
            print(f"     Previous: {block.previous_hash[:20]}...")
            print(f"     Transactions: {len(block.transactions)}")
            print(f"     Nonce: {block.nonce}")

class SimpleVotingSystem:
    """Simplified voting system for demonstration"""
    def __init__(self):
        self.blockchain = SimpleBlockchain()
        self.voters = {}
        self.elections = {}
        self.candidates = {}
    
    def register_voter(self, username: str, voter_id: str) -> None:
        """Register a new voter"""
        self.voters[username] = {
            'voter_id': voter_id,
            'registered_at': datetime.now()
        }
        print(f"👤 Voter registered: {username} (ID: {voter_id})")
    
    def create_election(self, election_id: str, title: str, candidates: List[str]) -> None:
        """Create a new election"""
        self.elections[election_id] = {
            'title': title,
            'candidates': candidates,
            'created_at': datetime.now(),
            'is_active': True
        }
        print(f"🗳️  Election created: {title}")
        print(f"   Candidates: {', '.join(candidates)}")
    
    def cast_vote(self, username: str, election_id: str, candidate: str) -> None:
        """Cast a vote in an election"""
        if username not in self.voters:
            print(f"❌ Voter {username} not registered")
            return
        
        if election_id not in self.elections:
            print(f"❌ Election {election_id} not found")
            return
        
        if candidate not in self.elections[election_id]['candidates']:
            print(f"❌ Candidate {candidate} not found in election")
            return
        
        # Add vote transaction to blockchain
        self.blockchain.add_transaction(
            sender=self.voters[username]['voter_id'],
            recipient='ELECTION_SYSTEM',
            data={
                'type': 'vote',
                'election_id': election_id,
                'candidate': candidate,
                'voter_id': self.voters[username]['voter_id']
            }
        )
        
        print(f"✅ Vote cast: {username} voted for {candidate}")
    
    def get_results(self, election_id: str) -> None:
        """Get and display election results"""
        if election_id not in self.elections:
            print(f"❌ Election {election_id} not found")
            return
        
        results = self.blockchain.get_election_results(election_id)
        election = self.elections[election_id]
        
        print(f"\n📊 Election Results: {election['title']}")
        print(f"   Total votes: {results['total_votes']}")
        
        if results['vote_counts']:
            print(f"\n   Vote breakdown:")
            for candidate, votes in results['vote_counts'].items():
                percentage = (votes / results['total_votes']) * 100
                print(f"     {candidate}: {votes} votes ({percentage:.1f}%)")
        else:
            print("   No votes cast yet")

def run_demo():
    """Run a complete demonstration of the voting system"""
    print("🚀 Blockchain Voting System Demo")
    print("=" * 50)
    
    # Initialize the voting system
    voting_system = SimpleVotingSystem()
    
    # Register voters
    print("\n👥 Registering Voters...")
    voting_system.register_voter("alice", "VOTER001")
    voting_system.register_voter("bob", "VOTER002")
    voting_system.register_voter("charlie", "VOTER003")
    voting_system.register_voter("diana", "VOTER004")
    
    # Create an election
    print("\n🗳️  Creating Election...")
    voting_system.create_election(
        "PRESIDENT_2024",
        "Presidential Election 2024",
        ["John Smith", "Jane Doe", "Mike Johnson"]
    )
    
    # Cast votes
    print("\n🗳️  Casting Votes...")
    voting_system.cast_vote("alice", "PRESIDENT_2024", "John Smith")
    voting_system.cast_vote("bob", "PRESIDENT_2024", "Jane Doe")
    voting_system.cast_vote("charlie", "PRESIDENT_2024", "John Smith")
    voting_system.cast_vote("diana", "PRESIDENT_2024", "Mike Johnson")
    
    # Mine the transactions
    print("\n⛏️  Mining Transactions...")
    voting_system.blockchain.mine_pending_transactions("DEMO_MINER")
    
    # Display blockchain status
    voting_system.blockchain.display_chain()
    
    # Get election results
    voting_system.get_results("PRESIDENT_2024")
    
    # Demonstrate blockchain integrity
    print(f"\n🔒 Blockchain Integrity Check:")
    print(f"   Valid: {voting_system.blockchain.is_chain_valid()}")
    
    # Show security features
    print(f"\n🛡️  Security Features:")
    print(f"   ✅ Cryptographic hashing (SHA-256)")
    print(f"   ✅ Proof of work consensus")
    print(f"   ✅ Immutable vote records")
    print(f"   ✅ Transparent audit trail")
    print(f"   ✅ Tamper-proof blockchain")
    
    print(f"\n🎉 Demo completed successfully!")
    print(f"\n📚 This demonstrates the core blockchain voting functionality.")
    print(f"   For the full web application, install dependencies and run 'python app.py'")

if __name__ == "__main__":
    run_demo() 