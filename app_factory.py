#!/usr/bin/env python3
"""
Application factory for the Blockchain Voting System
"""
from flask import Flask
from flask_login import LoginManager
from models import db, Voter
from blockchain import Blockchain
import threading
import time
import json
from datetime import datetime
from config import get_config, ProductionConfig
import os

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    config.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        try:
            voter = Voter.query.get(user_id)
            if voter:
                print(f"User loaded successfully: {voter.username}")
            return voter
        except Exception as e:
            print(f"Error loading user: {e}")
            return None
    
    # Initialize blockchain
    blockchain = Blockchain()
    
    # Register blueprints and routes
    register_routes(app, blockchain)
    
    # Initialize database
    init_database(app)
    
    # Start mining thread in production
    if (config is ProductionConfig) or (os.environ.get('FLASK_ENV') == 'production'):
        start_mining_thread(app, blockchain)
    
    return app

def register_routes(app, blockchain):
    """Register all application routes"""
    
    # Import route functions
    from routes import (
        # Test routes
        hello, simple, debug,
        # Main routes
        index, login, logout, register, register_simple,
        elections, election_detail, vote, results,
        # Admin routes
        admin_elections, admin_candidates, edit_candidate,
        delete_candidate, admin_blockchain,
        # Test routes
        test_simple, test_route, test_db, test_session,
        # Utility routes
        ping, health_check,
        # API routes
        api_blockchain, api_election_results
    )
    
    # Test routes
    app.add_url_rule('/hello', 'hello', hello, methods=['GET'])
    app.add_url_rule('/simple', 'simple', simple, methods=['GET'])
    app.add_url_rule('/debug', 'debug', debug, methods=['GET'])
    
    # Main routes
    app.add_url_rule('/', 'index', index, methods=['GET'])
    app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout, methods=['GET'])
    app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
    app.add_url_rule('/register-simple', 'register_simple', register_simple, methods=['GET', 'POST'])
    app.add_url_rule('/elections', 'elections', elections, methods=['GET'])
    app.add_url_rule('/election/<election_id>', 'election_detail', election_detail, methods=['GET'])
    app.add_url_rule('/vote/<election_id>', 'vote', vote, methods=['GET', 'POST'])
    app.add_url_rule('/results/<election_id>', 'results', results, methods=['GET'])
    
    # Admin routes
    app.add_url_rule('/admin/elections', 'admin_elections', admin_elections, methods=['GET', 'POST'])
    app.add_url_rule('/admin/election/<election_id>/candidates', 'admin_candidates', admin_candidates, methods=['GET', 'POST'])
    app.add_url_rule('/admin/election/<election_id>/candidate/<candidate_id>/edit', 'edit_candidate', edit_candidate, methods=['GET', 'POST'])
    app.add_url_rule('/admin/election/<election_id>/candidate/<candidate_id>/delete', 'delete_candidate', delete_candidate, methods=['POST'])
    app.add_url_rule('/admin/blockchain', 'admin_blockchain', admin_blockchain, methods=['GET', 'POST'])
    
    # Test routes
    app.add_url_rule('/test-simple', 'test_simple', test_simple, methods=['GET'])
    app.add_url_rule('/test', 'test_route', test_route, methods=['GET'])
    app.add_url_rule('/test-db', 'test_db', test_db, methods=['GET'])
    app.add_url_rule('/test-session', 'test_session', test_session, methods=['GET'])
    
    # Utility routes
    app.add_url_rule('/ping', 'ping', ping, methods=['GET'])
    app.add_url_rule('/health', 'health_check', health_check, methods=['GET'])
    
    # API routes
    app.add_url_rule('/api/blockchain', 'api_blockchain', api_blockchain, methods=['GET'])
    app.add_url_rule('/api/election/<election_id>/results', 'api_election_results', api_election_results, methods=['GET'])
    
    # Add blockchain to app context
    app.blockchain = blockchain

def init_database(app):
    """Initialize database tables"""
    with app.app_context():
        try:
            print("Starting database initialization...")
            
            # Log database URI (masked for security)
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_uri:
                # Mask password in URI for logging
                if '@' in db_uri:
                    masked_uri = db_uri.split('@')[0].split('://')[0] + '://***:***@' + '@'.join(db_uri.split('@')[1:])
                else:
                    masked_uri = db_uri
                print(f"Database URI: {masked_uri}")
            else:
                print("WARNING: No database URI configured!")
            
            # Ensure instance directory exists for SQLite
            if 'sqlite' in db_uri:
                import os
                instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
                if not os.path.exists(instance_path):
                    os.makedirs(instance_path)
                    print(f"Created instance directory: {instance_path}")
            
            db.create_all()
            print("Database tables created successfully")
            
            # Try to create initial blockchain state
            try:
                from models import BlockchainState
                if not BlockchainState.query.first():
                    print("Creating initial blockchain state...")
                    blockchain_state = BlockchainState()
                    db.session.add(blockchain_state)
                    db.session.commit()
                    print("Initial blockchain state created")
                else:
                    print("Blockchain state already exists")
            except Exception as e:
                print(f"Warning: Could not create blockchain state: {e}")
            
            print("Database initialization completed successfully")
            
        except Exception as e:
            print(f"Error during database initialization: {e}")
            raise

def start_mining_thread(app, blockchain):
    """Start blockchain mining thread"""
    def mine_pending_transactions():
        """Mine pending transactions in the background"""
        with app.app_context():
            while True:
                try:
                    from models import PendingTransaction, Vote, BlockchainState
                    
                    # Get pending transactions
                    pending_txs = PendingTransaction.query.all()
                    if pending_txs:
                        # Convert to blockchain format
                        for tx in pending_txs:
                            tx_data = json.loads(tx.data)
                            blockchain.add_transaction(tx.sender, tx.recipient, tx_data)
                        
                        # Mine the block
                        blockchain.mine_pending_transactions("SYSTEM_MINER")
                        
                        # Update vote records
                        for tx in pending_txs:
                            if tx.transaction_type == 'vote':
                                tx_data = json.loads(tx.data)
                                from models import Voter
                                voter = Voter.query.filter_by(voter_id=tx_data['voter_id']).first()
                                if voter:
                                    vote = Vote.query.filter_by(
                                        voter_id=voter.id,
                                        election_id=tx_data['election_id'],
                                        candidate_id=tx_data['candidate_id']
                                    ).first()
                                
                                if vote and not vote.transaction_hash:
                                    vote.transaction_hash = blockchain.get_latest_block().hash
                                    vote.block_index = len(blockchain.chain) - 1
                        
                        # Remove pending transactions
                        for tx in pending_txs:
                            db.session.delete(tx)
                        
                        # Update blockchain state
                        state = BlockchainState.query.first()
                        if state:
                            state.last_block_index = len(blockchain.chain) - 1
                            state.last_block_hash = blockchain.get_latest_block().hash
                            state.total_transactions += len(pending_txs)
                            state.last_updated = datetime.utcnow()
                        
                        db.session.commit()
                        print(f"Mined block {len(blockchain.chain) - 1} with {len(pending_txs)} transactions")
                    
                    # Sleep interval from config
                    sleep_interval = app.config.get('BLOCKCHAIN_MINING_INTERVAL', 10)
                    time.sleep(sleep_interval)
                    
                except Exception as e:
                    print(f"Error in mining: {e}")
                    time.sleep(30)
    
    # Start mining thread
    mining_thread = threading.Thread(target=mine_pending_transactions, daemon=True)
    mining_thread.start()
    print("Mining thread started")

# For backward compatibility - only create app if not imported as module
if __name__ == '__main__':
    app = create_app()
