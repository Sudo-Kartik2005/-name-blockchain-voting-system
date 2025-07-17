from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Voter, Election, Candidate, Vote, BlockchainState, PendingTransaction
from forms import RegistrationForm, LoginForm, ElectionForm, CandidateForm, EditCandidateForm, VoteForm, AdminForm
from blockchain import Blockchain
import json
import threading
import time
from datetime import datetime, timedelta
import os

app = Flask(__name__)
# Load secret key from environment variable for production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
if app.config['SECRET_KEY'] == 'your-secret-key-change-this-in-production':
    import warnings
    warnings.warn('WARNING: Using default SECRET_KEY! Set SECRET_KEY environment variable for production.')

# Use environment variable for database URI if set
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'voting_system.db')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize blockchain
blockchain = Blockchain()

# Custom Jinja2 filters
@app.template_filter('datetime')
def datetime_filter(timestamp):
    """Convert timestamp to readable datetime format"""
    if timestamp is None:
        return "N/A"
    try:
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(timestamp, datetime):
            return timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return str(timestamp)
    except:
        return str(timestamp)

@login_manager.user_loader
def load_user(user_id):
    return Voter.query.get(user_id)

def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        # Ensure instance directory exists
        instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        db.create_all()
        
        # Create initial blockchain state if it doesn't exist
        if not BlockchainState.query.first():
            blockchain_state = BlockchainState()
            db.session.add(blockchain_state)
            db.session.commit()

def mine_pending_transactions():
    """Mine pending transactions in the background"""
    with app.app_context():
        while True:
            try:
                # Get pending transactions from database
                pending_txs = PendingTransaction.query.all()
                if pending_txs:
                    # Convert to blockchain format
                    for tx in pending_txs:
                        tx_data = json.loads(tx.data)
                        blockchain.add_transaction(tx.sender, tx.recipient, tx_data)
                    
                    # Mine the block
                    blockchain.mine_pending_transactions("SYSTEM_MINER")
                    
                    # Get the latest block hash
                    latest_block = blockchain.get_latest_block()
                    block_hash = latest_block.hash
                    
                    # Update vote records with transaction hashes
                    for tx in pending_txs:
                        if tx.transaction_type == 'vote':
                            tx_data = json.loads(tx.data)
                            # Find the corresponding vote record
                            vote = Vote.query.filter_by(
                                voter_id=Voter.query.filter_by(voter_id=tx_data['voter_id']).first().id,
                                election_id=tx_data['election_id'],
                                candidate_id=tx_data['candidate_id']
                            ).first()
                            
                            if vote and not vote.transaction_hash:
                                vote.transaction_hash = block_hash
                                vote.block_index = len(blockchain.chain) - 1
                    
                    # Remove pending transactions
                    for tx in pending_txs:
                        db.session.delete(tx)
                    
                    # Update blockchain state
                    state = BlockchainState.query.first()
                    if state:
                        state.last_block_index = len(blockchain.chain) - 1
                        state.last_block_hash = block_hash
                        state.total_transactions += len(pending_txs)
                        state.last_updated = datetime.utcnow()
                    
                    db.session.commit()
                    print(f"Mined block {len(blockchain.chain) - 1} with {len(pending_txs)} transactions")
                
                time.sleep(10)  # Mine every 10 seconds
            except Exception as e:
                print(f"Error in mining: {e}")
                time.sleep(30)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Home page"""
    active_elections = Election.query.filter_by(is_active=True).all()
    return render_template('index.html', elections=active_elections)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Voter registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        voter = Voter(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            date_of_birth=form.date_of_birth.data,
            voter_id=form.voter_id.data
        )
        db.session.add(voter)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Voter login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        voter = Voter.query.filter_by(username=form.username.data).first()
        if voter and check_password_hash(voter.password_hash, form.password.data):
            login_user(voter, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Voter logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/elections')
def elections():
    """List all elections"""
    elections = Election.query.filter_by(is_active=True).order_by(Election.start_date.desc()).all()
    return render_template('elections.html', elections=elections, now=datetime.now())

@app.route('/election/<election_id>')
def election_detail(election_id):
    """Show election details and candidates"""
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    return render_template('election_detail.html', election=election, candidates=candidates, now=datetime.now())

@app.route('/vote/<election_id>', methods=['GET', 'POST'])
@login_required
def vote(election_id):
    """Cast a vote in an election"""
    election = Election.query.get_or_404(election_id)
    
    if not election.is_open:
        flash('This election is not currently open for voting.', 'error')
        return redirect(url_for('election_detail', election_id=election_id))
    
    # Check if user has already voted
    existing_vote = Vote.query.filter_by(voter_id=current_user.id, election_id=election_id).first()
    if existing_vote:
        flash('You have already voted in this election.', 'error')
        return redirect(url_for('election_detail', election_id=election_id))
    
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    form = VoteForm(candidates=candidates)
    
    if form.validate_on_submit():
        candidate = Candidate.query.get(form.candidate.data)
        
        # Create vote transaction
        vote_data = {
            'type': 'vote',
            'election_id': election_id,
            'candidate': candidate.name,
            'candidate_id': candidate.id,
            'voter_id': current_user.voter_id
        }
        
        # Add to pending transactions
        pending_tx = PendingTransaction(
            transaction_type='vote',
            sender=current_user.voter_id,
            recipient='ELECTION_SYSTEM',
            data=json.dumps(vote_data),
            timestamp=time.time()
        )
        db.session.add(pending_tx)
        
        # Create vote record (transaction_hash will be set after mining)
        vote = Vote(
            voter_id=current_user.id,
            election_id=election_id,
            candidate_id=candidate.id
        )
        db.session.add(vote)
        db.session.commit()
        
        flash('Your vote has been cast and will be added to the blockchain shortly.', 'success')
        return redirect(url_for('election_detail', election_id=election_id))
    
    return render_template('vote.html', form=form, election=election, candidates=candidates)

@app.route('/results/<election_id>')
def results(election_id):
    """Show election results"""
    election = Election.query.get_or_404(election_id)
    
    # Get results from blockchain
    blockchain_results = blockchain.get_election_results(election_id)
    
    # Get results from database
    votes = Vote.query.filter_by(election_id=election_id).all()
    candidate_votes = {}
    for vote in votes:
        candidate_name = vote.candidate.name
        candidate_votes[candidate_name] = candidate_votes.get(candidate_name, 0) + 1
    
    return render_template('results.html', 
                         election=election, 
                         blockchain_results=blockchain_results,
                         database_votes=candidate_votes)

@app.route('/admin/elections', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_elections():
    """Admin panel for managing elections"""
    if not current_user.is_authenticated:
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
    
    form = ElectionForm()
    if form.validate_on_submit():
        election = Election(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(election)
        db.session.commit()
        flash('Election created successfully!', 'success')
        return redirect(url_for('admin_elections'))
    
    elections = Election.query.order_by(Election.created_at.desc()).all()
    return render_template('admin_elections.html', form=form, elections=elections, now=datetime.now())

@app.route('/admin/election/<election_id>/candidates', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_candidates(election_id):
    """Manage candidates for an election"""
    election = Election.query.get_or_404(election_id)
    form = CandidateForm()
    
    if form.validate_on_submit():
        candidate = Candidate(
            name=form.name.data,
            party=form.party.data,
            description=form.description.data,
            election_id=election_id
        )
        db.session.add(candidate)
        db.session.commit()
        flash('Candidate added successfully!', 'success')
        return redirect(url_for('admin_candidates', election_id=election_id))
    
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    return render_template('admin_candidates.html', form=form, election=election, candidates=candidates)

@app.route('/admin/election/<election_id>/candidate/<candidate_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_candidate(election_id, candidate_id):
    """Edit a candidate"""
    election = Election.query.get_or_404(election_id)
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Ensure candidate belongs to this election
    if candidate.election_id != election_id:
        flash('Candidate not found in this election.', 'error')
        return redirect(url_for('admin_candidates', election_id=election_id))
    
    form = EditCandidateForm(obj=candidate)
    
    if form.validate_on_submit():
        candidate.name = form.name.data
        candidate.party = form.party.data
        candidate.description = form.description.data
        db.session.commit()
        flash('Candidate updated successfully!', 'success')
        return redirect(url_for('admin_candidates', election_id=election_id))
    
    return render_template('edit_candidate.html', form=form, election=election, candidate=candidate)

@app.route('/admin/election/<election_id>/candidate/<candidate_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_candidate(election_id, candidate_id):
    """Delete a candidate"""
    election = Election.query.get_or_404(election_id)
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Ensure candidate belongs to this election
    if candidate.election_id != election_id:
        flash('Candidate not found in this election.', 'error')
        return redirect(url_for('admin_candidates', election_id=election_id))
    
    # Check if there are any votes for this candidate
    vote_count = Vote.query.filter_by(candidate_id=candidate_id).count()
    if vote_count > 0:
        flash(f'Cannot delete candidate. There are {vote_count} vote(s) cast for this candidate.', 'error')
        return redirect(url_for('admin_candidates', election_id=election_id))
    
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted successfully!', 'success')
    return redirect(url_for('admin_candidates', election_id=election_id))

@app.route('/admin/blockchain', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_blockchain():
    """Admin panel for blockchain management"""
    form = AdminForm()
    
    if form.validate_on_submit():
        if form.action.data == 'mine':
            # Trigger mining
            pending_txs = PendingTransaction.query.all()
            if pending_txs:
                for tx in pending_txs:
                    tx_data = json.loads(tx.data)
                    blockchain.add_transaction(tx.sender, tx.recipient, tx_data)
                
                blockchain.mine_pending_transactions("ADMIN_MINER")
                
                # Update database
                for tx in pending_txs:
                    db.session.delete(tx)
                
                state = BlockchainState.query.first()
                if state:
                    state.last_block_index = len(blockchain.chain) - 1
                    state.last_block_hash = blockchain.get_latest_block().hash
                    state.total_transactions += len(pending_txs)
                    state.last_updated = datetime.utcnow()
                
                db.session.commit()
                flash(f'Mined block {len(blockchain.chain) - 1} with {len(pending_txs)} transactions', 'success')
            else:
                flash('No pending transactions to mine', 'info')
        
        elif form.action.data == 'validate':
            is_valid = blockchain.is_chain_valid()
            if is_valid:
                flash('Blockchain is valid!', 'success')
            else:
                flash('Blockchain validation failed!', 'error')
        
        elif form.action.data == 'export':
            # Export blockchain data
            blockchain_data = blockchain.to_dict()
            return jsonify(blockchain_data)
    
    # Get blockchain stats
    state = BlockchainState.query.first()
    pending_count = PendingTransaction.query.count()
    
    return render_template('admin_blockchain.html', 
                         form=form, 
                         state=state, 
                         pending_count=pending_count,
                         chain_length=len(blockchain.chain))

@app.route('/api/blockchain')
def api_blockchain():
    """API endpoint to get blockchain data"""
    return jsonify(blockchain.to_dict())

@app.route('/api/election/<election_id>/results')
def api_election_results(election_id):
    """API endpoint to get election results"""
    results = blockchain.get_election_results(election_id)
    return jsonify(results)

@app.route('/admin/login', methods=['GET', 'POST'])
@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('admin_elections'))

    form = LoginForm()
    if form.validate_on_submit():
        voter = Voter.query.filter_by(username=form.username.data).first()
        if voter and voter.is_admin and check_password_hash(voter.password_hash, form.password.data):
            login_user(voter, remember=form.remember_me.data)
            return redirect(url_for('admin_elections'))
        else:
            flash('Invalid admin credentials', 'error')
    return render_template('admin_login.html', form=form)

# Initialize database when app starts (for deployment)
with app.app_context():
    init_db()

if __name__ == '__main__':
    # Start mining thread
    mining_thread = threading.Thread(target=mine_pending_transactions, daemon=True)
    mining_thread.start()
    
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port) 