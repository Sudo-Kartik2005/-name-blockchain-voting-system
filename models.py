from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()

class Voter(UserMixin, db.Model):
    """Voter model for authentication and voter management"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    voter_id = db.Column(db.String(20), unique=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with votes
    votes = db.relationship('Vote', backref='voter', lazy=True)
    
    def __repr__(self):
        return f'<Voter {self.username}>'

class Election(db.Model):
    """Election model for managing elections"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with candidates and votes
    candidates = db.relationship('Candidate', backref='election', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='election', lazy=True)
    
    def __repr__(self):
        return f'<Election {self.title}>'
    
    @property
    def is_open(self):
        """Check if the election is currently open for voting"""
        from datetime import datetime
        now = datetime.now()
        return self.start_date <= now <= self.end_date and self.is_active

class Candidate(db.Model):
    """Candidate model for election candidates"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    election_id = db.Column(db.String(36), db.ForeignKey('election.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with votes
    votes = db.relationship('Vote', backref='candidate', lazy=True)
    
    def __repr__(self):
        return f'<Candidate {self.name}>'

class Vote(db.Model):
    """Vote model for tracking votes in the blockchain"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    voter_id = db.Column(db.String(36), db.ForeignKey('voter.id'), nullable=False)
    election_id = db.Column(db.String(36), db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidate.id'), nullable=False)
    transaction_hash = db.Column(db.String(64), unique=True, nullable=True)
    block_index = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vote {self.id}>'

class BlockchainState(db.Model):
    """Model for storing blockchain state and metadata"""
    id = db.Column(db.Integer, primary_key=True)
    last_block_index = db.Column(db.Integer, default=0)
    last_block_hash = db.Column(db.String(64), nullable=True)
    total_transactions = db.Column(db.Integer, default=0)
    chain_valid = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlockchainState {self.last_block_index}>'

class PendingTransaction(db.Model):
    """Model for storing pending transactions before mining"""
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_type = db.Column(db.String(50), nullable=False)  # 'vote', 'election_creation', etc.
    sender = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    data = db.Column(db.Text, nullable=False)  # JSON string
    timestamp = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PendingTransaction {self.id}>' 