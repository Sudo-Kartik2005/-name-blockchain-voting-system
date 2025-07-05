import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import uuid

class Block:
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary for JSON serialization"""
        return {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.difficulty = 4
        self.pending_transactions: List[Dict] = []
        self.mining_reward = 10
        
        # Create the genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = Block(0, [], time.time(), "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1]
    
    def add_transaction(self, sender: str, recipient: str, data: Dict) -> int:
        """Add a new transaction to pending transactions"""
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'data': data,
            'timestamp': time.time(),
            'transaction_id': str(uuid.uuid4())
        }
        self.pending_transactions.append(transaction)
        return self.get_latest_block().index + 1
    
    def mine_pending_transactions(self, miner_address: str) -> None:
        """Mine all pending transactions and add them to the blockchain"""
        if not self.pending_transactions:
            return
        
        # Create a new block with all pending transactions
        block = Block(
            len(self.chain),
            self.pending_transactions,
            time.time(),
            self.get_latest_block().hash
        )
        
        # Mine the block
        block.mine_block(self.difficulty)
        
        # Add the block to the chain
        self.chain.append(block)
        
        # Reset pending transactions and add mining reward
        self.pending_transactions = [
            {
                'sender': "BLOCKCHAIN_REWARD",
                'recipient': miner_address,
                'data': {'type': 'mining_reward', 'amount': self.mining_reward},
                'timestamp': time.time(),
                'transaction_id': str(uuid.uuid4())
            }
        ]
    
    def is_chain_valid(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if the current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if the previous hash reference is correct
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_balance(self, address: str) -> int:
        """Calculate the balance of a given address"""
        balance = 0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['recipient'] == address:
                    balance += transaction['data'].get('amount', 0)
                if transaction['sender'] == address and transaction['sender'] != "BLOCKCHAIN_REWARD":
                    balance -= transaction['data'].get('amount', 0)
        
        return balance
    
    def get_vote_count(self, election_id: str) -> Dict[str, int]:
        """Count votes for a specific election"""
        vote_counts = {}
        
        for block in self.chain:
            for transaction in block.transactions:
                if (transaction['data'].get('type') == 'vote' and 
                    transaction['data'].get('election_id') == election_id):
                    candidate = transaction['data'].get('candidate')
                    if candidate:
                        vote_counts[candidate] = vote_counts.get(candidate, 0) + 1
        
        return vote_counts
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert blockchain to dictionary for JSON serialization"""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': self.pending_transactions,
            'difficulty': self.difficulty,
            'mining_reward': self.mining_reward
        } 