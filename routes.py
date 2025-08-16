#!/usr/bin/env python3
"""
Route functions for the Blockchain Voting System
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Voter, Election, Candidate, Vote, BlockchainState, PendingTransaction
from forms import RegistrationForm, LoginForm, ElectionForm, CandidateForm, EditCandidateForm, VoteForm, AdminForm
from datetime import datetime, timedelta
import json

# Test routes
def hello():
    return "Hello! The app is working!"

def simple():
    return "SUCCESS: Basic Flask route is working!"

def debug():
    from flask import current_app
    return f"""
    <h1>Debug Information</h1>
    <p>App is running!</p>
    <p>Timestamp: {datetime.utcnow()}</p>
    <p>Database URI: {current_app.config['SQLALCHEMY_DATABASE_URI'].replace('://', '://***:***@') if '@' in current_app.config['SQLALCHEMY_DATABASE_URI'] else current_app.config['SQLALCHEMY_DATABASE_URI']}</p>
    <p>Available routes:</p>
    <ul>
        <li><a href="/hello">/hello</a></li>
        <li><a href="/ping">/ping</a></li>
        <li><a href="/test">/test</a></li>
        <li><a href="/test-simple">/test-simple</a></li>
        <li><a href="/register-simple">/register-simple</a></li>
    </ul>
    """

# Main routes
def index():
    """Main page - redirects to elections or login"""
    if current_user.is_authenticated:
        return redirect(url_for('elections'))
    else:
        return redirect(url_for('login'))

def ping():
    """Health check endpoint"""
    try:
        from flask import current_app
        database_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected' if 'sqlite' in database_uri or 'postgresql' in database_uri else 'disconnected'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def register_simple():
    """Simple registration form"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not username or not password or not email:
            flash('All fields are required', 'error')
            return render_template('register_simple.html')
        
        # Check if user already exists
        existing_user = Voter.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register_simple.html')
        
        # Create new user
        new_voter = Voter(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            is_admin=False
        )
        
        try:
            db.session.add(new_voter)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register_simple.html')
    
    return render_template('register_simple.html')

def register():
    """Full registration form"""
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = Voter.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        new_voter = Voter(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            is_admin=False
        )
        
        try:
            db.session.add(new_voter)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('register.html', form=form)
    
    return render_template('register.html', form=form)

def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        voter = Voter.query.filter_by(username=form.username.data).first()
        if voter and check_password_hash(voter.password_hash, form.password.data):
            login_user(voter, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('elections')
            return redirect(next_page)
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))

def elections():
    """List all elections"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    elections_list = Election.query.all()
    return render_template('elections.html', elections=elections_list)

def election_detail(election_id):
    """Show election details"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    return render_template('election_detail.html', election=election, candidates=candidates)

def vote(election_id):
    """Vote in an election"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    election = Election.query.get_or_404(election_id)
    
    # Check if user already voted
    existing_vote = Vote.query.filter_by(
        voter_id=current_user.id,
        election_id=election_id
    ).first()
    
    if existing_vote:
        flash('You have already voted in this election', 'error')
        return redirect(url_for('election_detail', election_id=election_id))
    
    form = VoteForm()
    form.candidate_id.choices = [(c.id, c.name) for c in Candidate.query.filter_by(election_id=election_id).all()]
    
    if form.validate_on_submit():
        # Create vote record
        new_vote = Vote(
            voter_id=current_user.id,
            election_id=election_id,
            candidate_id=form.candidate_id.data,
            timestamp=datetime.utcnow()
        )
        
        try:
            db.session.add(new_vote)
            db.session.commit()
            flash('Vote recorded successfully!', 'success')
            return redirect(url_for('results', election_id=election_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Vote failed: {str(e)}', 'error')
    
    return render_template('vote.html', form=form, election=election)

def results(election_id):
    """Show election results"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    
    # Calculate vote counts
    for candidate in candidates:
        candidate.vote_count = Vote.query.filter_by(candidate_id=candidate.id).count()
    
    return render_template('results.html', election=election, candidates=candidates)

# Admin routes
def admin_elections():
    """Admin: Manage elections"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    form = ElectionForm()
    if form.validate_on_submit():
        new_election = Election(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        
        try:
            db.session.add(new_election)
            db.session.commit()
            flash('Election created successfully!', 'success')
            return redirect(url_for('admin_elections'))
        except Exception as e:
            db.session.rollback()
            flash(f'Election creation failed: {str(e)}', 'error')
    
    elections_list = Election.query.all()
    return render_template('admin_elections.html', form=form, elections=elections_list)

def admin_candidates(election_id):
    """Admin: Manage candidates for an election"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    election = Election.query.get_or_404(election_id)
    form = CandidateForm()
    
    if form.validate_on_submit():
        new_candidate = Candidate(
            name=form.name.data,
            party=form.party.data,
            election_id=election_id
        )
        
        try:
            db.session.add(new_candidate)
            db.session.commit()
            flash('Candidate added successfully!', 'success')
            return redirect(url_for('admin_candidates', election_id=election_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Candidate addition failed: {str(e)}', 'error')
    
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    return render_template('admin_candidates.html', form=form, election=election, candidates=candidates)

def edit_candidate(election_id, candidate_id):
    """Admin: Edit a candidate"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    candidate = Candidate.query.get_or_404(candidate_id)
    form = EditCandidateForm(obj=candidate)
    
    if form.validate_on_submit():
        candidate.name = form.name.data
        candidate.party = form.party.data
        
        try:
            db.session.commit()
            flash('Candidate updated successfully!', 'success')
            return redirect(url_for('admin_candidates', election_id=election_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Candidate update failed: {str(e)}', 'error')
    
    return render_template('edit_candidate.html', form=form, candidate=candidate, election_id=election_id)

def delete_candidate(election_id, candidate_id):
    """Admin: Delete a candidate"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    candidate = Candidate.query.get_or_404(candidate_id)
    
    try:
        db.session.delete(candidate)
        db.session.commit()
        flash('Candidate deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Candidate deletion failed: {str(e)}', 'error')
    
    return redirect(url_for('admin_candidates', election_id=election_id))

def admin_blockchain():
    """Admin: View blockchain status"""
    if not current_user.is_authenticated or not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get blockchain state
    blockchain_state = BlockchainState.query.first()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'mine':
            # Trigger mining
            flash('Mining triggered', 'info')
    
    return render_template('admin_blockchain.html', blockchain_state=blockchain_state)

# Test routes
def test_simple():
    return "SUCCESS: Test route is working!"

def test_route():
    return f"""
    <h1>Test Route</h1>
    <p>Current time: {datetime.utcnow()}</p>
    <p>User authenticated: {current_user.is_authenticated}</p>
    <p>User: {current_user.username if current_user.is_authenticated else 'Not logged in'}</p>
    """

def test_db():
    """Test database connection and show voter count"""
    try:
        voter_count = Voter.query.count()
        voters = Voter.query.limit(5).all()
        
        result = f"""
        <h1>Database Test</h1>
        <p>✅ Database connection: SUCCESS</p>
        <p>📊 Total voters: {voter_count}</p>
        <p>👥 Sample voters:</p>
        <ul>
        """
        
        for voter in voters:
            result += f"<li>{voter.username} (ID: {voter.id})</li>"
        
        result += "</ul>"
        return result
        
    except Exception as e:
        return f"""
        <h1>Database Test</h1>
        <p>❌ Database connection: FAILED</p>
        <p>Error: {str(e)}</p>
        """

def test_session():
    """Test session and authentication"""
    return f"""
    <h1>Session Test</h1>
    <p>Session ID: {session.get('_id', 'Not set')}</p>
    <p>Session data: {dict(session)}</p>
    <p>User authenticated: {current_user.is_authenticated}</p>
    <p>User: {current_user.username if current_user.is_authenticated else 'Not logged in'}</p>
    """

def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

# API routes
def api_blockchain():
    """API endpoint for blockchain data"""
    try:
        blockchain_state = BlockchainState.query.first()
        if blockchain_state:
            return jsonify({
                'last_block_index': blockchain_state.last_block_index,
                'last_block_hash': blockchain_state.last_block_hash,
                'total_transactions': blockchain_state.total_transactions,
                'last_updated': blockchain_state.last_updated.isoformat() if blockchain_state.last_updated else None
            })
        else:
            return jsonify({'error': 'Blockchain state not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def api_election_results(election_id):
    """API endpoint for election results"""
    try:
        election = Election.query.get_or_404(election_id)
        candidates = Candidate.query.filter_by(election_id=election_id).all()
        
        results = []
        for candidate in candidates:
            vote_count = Vote.query.filter_by(candidate_id=candidate.id).count()
            results.append({
                'candidate_id': candidate.id,
                'name': candidate.name,
                'party': candidate.party,
                'vote_count': vote_count
            })
        
        return jsonify({
            'election_id': election.id,
            'title': election.title,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
