from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
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
from flask_mail import Mail, Message

app = Flask(__name__)
# Load secret key from environment variable for production
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
if app.config['SECRET_KEY'] == 'your-secret-key-change-this-in-production':
    import warnings
    warnings.warn('WARNING: Using default SECRET_KEY! Set SECRET_KEY environment variable for production.')

# Use environment variable for database URI if set
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Handle Render's PostgreSQL URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'voting_system.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Flask-Mail
mail = Mail()
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-mailtrap-username')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-mailtrap-password')
app.config['MAIL_DISABLED'] = os.environ.get('MAIL_DISABLED', 'false').lower() == 'true'
mail.init_app(app)

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

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    print(f"Internal Server Error: {error}")
    try:
        db.session.rollback()
    except:
        pass
    return "Internal Server Error - Please try again later", 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return "Page Not Found", 404

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions"""
    print(f"Unhandled exception: {e}")
    try:
        db.session.rollback()
    except:
        pass
    return "An unexpected error occurred", 500

@login_manager.user_loader
def load_user(user_id):
    return Voter.query.get(user_id)

def init_db():
    """Initialize the database with tables"""
    try:
        with app.app_context():
            print("Starting database initialization...")
            
            # Ensure instance directory exists
            instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
            if not os.path.exists(instance_path):
                os.makedirs(instance_path)
                print(f"Created instance directory: {instance_path}")
            
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully")
            
            # Try to create initial blockchain state if it doesn't exist
            try:
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
                # Continue without blockchain state - it's not critical for basic functionality
            
            print("Database initialization completed successfully")
            
    except Exception as e:
        print(f"Error during database initialization: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Try to create tables without the blockchain state
        try:
            print("Attempting basic database initialization...")
            with app.app_context():
                db.create_all()
                print("Basic database tables created (blockchain state creation failed)")
        except Exception as e2:
            print(f"Critical database initialization error: {e2}")
            print(f"Error type: {type(e2).__name__}")
            import traceback
            traceback.print_exc()
            raise

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
                            voter = Voter.query.filter_by(voter_id=tx_data['voter_id']).first()
                            if voter:
                                vote = Vote.query.filter_by(
                                    voter_id=voter.id,
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

@app.route('/')
def index():
    """Home page"""
    active_elections = Election.query.filter_by(is_active=True).all()
    return render_template('index.html', elections=active_elections)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Voter registration with OTP verification"""
    print("=== Registration Route Called ===")
    try:
        if current_user.is_authenticated:
            print("User already authenticated, redirecting to index")
            return redirect(url_for('index'))
        
        print("Creating registration form")
        form = RegistrationForm()
        
        if request.method == 'POST':
            print("POST request received")
            print(f"Form data: {request.form}")
            
            if form.validate_on_submit():
                print("Form validation passed")
                try:
                    import random
                    otp = str(random.randint(100000, 999999))
                    print(f"Generated OTP: {otp}")
                    
                    # Validate date_of_birth before storing in session
                    if not form.date_of_birth.data:
                        print("Date of birth is missing")
                        flash('Date of birth is required.', 'error')
                        return render_template('register.html', form=form)
                    
                    print("Storing registration data in session")
                    # Store registration data and OTP in session
                    session['registration_data'] = {
                        'username': form.username.data,
                        'email': form.email.data,
                        'password_hash': generate_password_hash(form.password.data),
                        'first_name': form.first_name.data,
                        'last_name': form.last_name.data,
                        'date_of_birth': form.date_of_birth.data.isoformat(),
                        'voter_id': form.voter_id.data
                    }
                    session['otp'] = otp
                    session['otp_email'] = form.email.data
                    
                    print("Session data stored successfully")
                    
                    # Send OTP email via Mailtrap
                    if app.config.get('MAIL_DISABLED', False):
                        # Email disabled for development/production
                        print("Email disabled, showing OTP in flash message")
                        flash(f'Email disabled. Your OTP is: {otp}', 'info')
                    else:
                        try:
                            print("Attempting to send email")
                            msg = Message('Your OTP Code', recipients=[form.email.data])
                            msg.body = f'Your OTP code for registration is: {otp}'
                            mail.send(msg)
                            flash('An OTP has been sent to your email. Please enter it to complete registration.', 'info')
                            print("Email sent successfully")
                        except Exception as e:
                            # Fallback: store OTP in session and show it to user
                            print(f"Email sending failed: {e}")
                            flash(f'Email sending failed. Your OTP is: {otp}', 'warning')
                    
                    print("Redirecting to OTP verification")
                    return redirect(url_for('verify_otp'))
                    
                except Exception as e:
                    print(f"Error in registration form processing: {e}")
                    print(f"Error type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
                    flash('An error occurred during registration. Please try again.', 'error')
                    return render_template('register.html', form=form)
            else:
                print("Form validation failed")
                print(f"Form errors: {form.errors}")
        
        print("Rendering registration template")
        return render_template('register.html', form=form)
        
    except Exception as e:
        print(f"Critical error in registration route: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        flash('A system error occurred. Please try again later.', 'error')
        return render_template('register.html', form=RegistrationForm())

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """OTP verification for registration"""
    try:
        if 'registration_data' not in session or 'otp' not in session:
            flash('No registration in progress. Please register again.', 'error')
            return redirect(url_for('register'))
        
        if request.method == 'POST':
            try:
                entered_otp = request.form.get('otp')
                if entered_otp == session.get('otp'):
                    # Complete registration
                    data = session['registration_data']
                    
                    try:
                        # Convert date string to Python date object
                        from datetime import date
                        date_of_birth = date.fromisoformat(data['date_of_birth'])
                        
                        # Check if user already exists
                        existing_voter = Voter.query.filter_by(username=data['username']).first()
                        if existing_voter:
                            flash('Username already exists. Please try again.', 'error')
                            return redirect(url_for('register'))
                        
                        existing_email = Voter.query.filter_by(email=data['email']).first()
                        if existing_email:
                            flash('Email already registered. Please try again.', 'error')
                            return redirect(url_for('register'))
                        
                        existing_voter_id = Voter.query.filter_by(voter_id=data['voter_id']).first()
                        if existing_voter_id:
                            flash('Voter ID already registered. Please try again.', 'error')
                            return redirect(url_for('register'))
                        
                        voter = Voter(
                            username=data['username'],
                            email=data['email'],
                            password_hash=data['password_hash'],
                            first_name=data['first_name'],
                            last_name=data['last_name'],
                            date_of_birth=date_of_birth,
                            voter_id=data['voter_id']
                        )
                        db.session.add(voter)
                        db.session.commit()
                        
                        # Clear session
                        session.pop('registration_data', None)
                        session.pop('otp', None)
                        session.pop('otp_email', None)
                        
                        flash('Registration successful! Please log in.', 'success')
                        return redirect(url_for('login'))
                        
                    except Exception as e:
                        print(f"Database error during voter creation: {e}")
                        db.session.rollback()
                        flash('An error occurred while creating your account. Please try again.', 'error')
                        return render_template('verify_otp.html')
                        
                else:
                    flash('Invalid OTP. Please try again.', 'error')
                    
            except Exception as e:
                print(f"Error in OTP verification: {e}")
                flash('An error occurred during verification. Please try again.', 'error')
                
        return render_template('verify_otp.html')
        
    except Exception as e:
        print(f"Critical error in OTP verification route: {e}")
        flash('A system error occurred. Please try again later.', 'error')
        return redirect(url_for('register'))

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
def admin_elections():
    """Admin panel for managing elections"""
    if not current_user.is_admin:
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
def admin_candidates(election_id):
    """Manage candidates for an election"""
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
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
def edit_candidate(election_id, candidate_id):
    """Edit a candidate"""
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
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
def delete_candidate(election_id, candidate_id):
    """Delete a candidate"""
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
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
def admin_blockchain():
    """Admin panel for blockchain management"""
    if not current_user.is_admin:
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))
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
    
    # Get blockchain data for display
    chain_data = [block.to_dict() for block in blockchain.chain]
    
    return render_template('admin_blockchain.html', 
                         form=form, 
                         state=state, 
                         pending_count=pending_count,
                         chain_length=len(blockchain.chain),
                         chain_data=chain_data)

@app.route('/test')
def test_route():
    """Simple test route to verify application is working"""
    return jsonify({
        'message': 'Application is working!',
        'timestamp': datetime.utcnow().isoformat(),
        'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else app.config['SQLALCHEMY_DATABASE_URI']
    })

@app.route('/health')
def health_check():
    """Health check endpoint for debugging"""
    try:
        # Test database connection
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/blockchain')
def api_blockchain():
    """API endpoint to get blockchain data"""
    return jsonify(blockchain.to_dict())

@app.route('/api/election/<election_id>/results')
def api_election_results(election_id):
    """API endpoint to get election results"""
    results = blockchain.get_election_results(election_id)
    return jsonify(results)

# Initialize database when app starts (for deployment)
with app.app_context():
    init_db()

if __name__ == '__main__':
    # Start mining thread
    mining_thread = threading.Thread(target=mine_pending_transactions, daemon=True)
    mining_thread.start()
    
    # Get port from environment variable (for deployment)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port) 