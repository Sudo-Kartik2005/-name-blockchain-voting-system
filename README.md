# Blockchain Voting System

A secure, transparent, and tamper-proof voting system built with Python, Flask, and blockchain technology. This system ensures that votes are cryptographically secured, immutable, and verifiable while maintaining voter anonymity.

## 🚀 Features

### Core Features
- **Blockchain-based Voting**: All votes are recorded on a cryptographic blockchain
- **Voter Registration**: Secure voter registration with unique voter IDs
- **Election Management**: Create and manage elections with multiple candidates
- **Real-time Results**: Live vote counting and result visualization
- **Cryptographic Security**: SHA-256 hashing and blockchain validation
- **Audit Trail**: Complete transparency with immutable vote records

### Security Features
- **One Vote Per Voter**: Prevents duplicate voting
- **Immutable Records**: Votes cannot be altered once recorded
- **Cryptographic Verification**: Blockchain integrity validation
- **Anonymous Voting**: Voter privacy while maintaining verifiability
- **Tamper-proof**: Distributed ledger prevents vote manipulation

### User Interface
- **Modern Web Interface**: Responsive design with Bootstrap 5
- **Real-time Updates**: Live blockchain status and vote counts
- **Interactive Voting**: Intuitive candidate selection interface
- **Admin Panel**: Comprehensive election management tools
- **Mobile Responsive**: Works on all devices

## 🛠️ Technology Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Blockchain**: Custom implementation with SHA-256 hashing
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login with password hashing
- **Forms**: Flask-WTF with validation

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blockchain-voting-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📖 Usage Guide

### For Voters

1. **Registration**
   - Visit the registration page
   - Fill in your personal information
   - Create a unique username and password
   - Provide a valid voter ID

2. **Login**
   - Use your username and password to log in
   - Access available elections

3. **Voting**
   - Browse active elections
   - Select your preferred candidate
   - Confirm your vote
   - Your vote is automatically added to the blockchain

4. **Viewing Results**
   - Check real-time election results
   - View blockchain verification data

### For Administrators

1. **Creating Elections**
   - Access the admin panel
   - Set election title and description
   - Configure start and end dates
   - Add candidates

2. **Managing Candidates**
   - Add candidate names and parties
   - Include candidate descriptions
   - Edit existing candidate information
   - Delete candidates (if no votes cast)
   - Update candidate details in real-time

3. **Blockchain Management**
   - Monitor blockchain status
   - Validate blockchain integrity
   - Export blockchain data
   - Mine pending transactions

## 🏗️ System Architecture

### Core Components

1. **Blockchain Module** (`blockchain.py`)
   - Block creation and mining
   - Transaction management
   - Chain validation
   - Cryptographic hashing

2. **Database Models** (`models.py`)
   - Voter registration
   - Election management
   - Candidate information
   - Vote tracking

3. **Web Application** (`app.py`)
   - Flask routes and views
   - User authentication
   - Form handling
   - API endpoints

4. **Forms** (`forms.py`)
   - User registration
   - Election creation
   - Voting interface
   - Admin controls

### Database Schema

- **Voters**: User accounts and authentication
- **Elections**: Election metadata and scheduling
- **Candidates**: Candidate information and parties
- **Votes**: Vote records and blockchain references
- **BlockchainState**: System status and metadata
- **PendingTransactions**: Unmined transactions

## 🔒 Security Implementation

### Cryptographic Security
- **SHA-256 Hashing**: All blocks use SHA-256 for integrity
- **Proof of Work**: Mining difficulty prevents tampering
- **Chain Validation**: Continuous blockchain integrity checks
- **Transaction Signing**: Secure vote transaction creation

### Access Control
- **Password Hashing**: Secure password storage with Werkzeug
- **Session Management**: Flask-Login for user sessions
- **Form Validation**: CSRF protection and input validation
- **Voter Verification**: Unique voter ID validation

### Data Integrity
- **Immutable Records**: Once recorded, votes cannot be changed
- **Audit Trail**: Complete transaction history
- **Blockchain Validation**: Regular integrity checks
- **Backup Systems**: Database and blockchain state tracking

## 📊 API Endpoints

### Public APIs
- `GET /api/blockchain` - Get blockchain data
- `GET /api/election/<id>/results` - Get election results

### Admin APIs
- `POST /admin/blockchain` - Blockchain management actions
- `GET /admin/elections` - Election management
- `POST /admin/election/<id>/candidates` - Add new candidates
- `GET /admin/election/<id>/candidate/<candidate_id>/edit` - Edit candidate
- `POST /admin/election/<id>/candidate/<candidate_id>/edit` - Update candidate
- `POST /admin/election/<id>/candidate/<candidate_id>/delete` - Delete candidate

## 👥 Candidate Management

### Features
- **Edit Candidate Details**: Update names, parties, and descriptions
- **Delete Candidates**: Remove candidates (only if no votes cast)
- **Real-time Updates**: Changes are immediately reflected
- **Safety Checks**: Prevents deletion of candidates with existing votes
- **User-friendly Interface**: Intuitive edit and delete buttons

### How to Use

1. **Access Candidate Management**
   - Go to Admin Panel → Elections
   - Click the "Manage Candidates" button for any election

2. **Edit a Candidate**
   - Click the edit (✏️) button next to any candidate
   - Modify the name, party, or description
   - Click "Update Candidate" to save changes

3. **Delete a Candidate**
   - Click the delete (🗑️) button next to any candidate
   - Confirm the deletion in the modal dialog
   - Note: Candidates with votes cannot be deleted

### Safety Features
- **Vote Protection**: Candidates with existing votes cannot be deleted
- **Confirmation Dialogs**: Delete operations require confirmation
- **Breadcrumb Navigation**: Easy navigation between pages
- **Error Handling**: Clear error messages for invalid operations

## 🧪 Testing

### Manual Testing
1. Register a new voter account
2. Create an election as admin
3. Add candidates to the election
4. Edit candidate details
5. Try to delete candidates (with and without votes)
6. Cast votes from different accounts
7. Verify blockchain integrity
8. Check election results

### Automated Testing
```bash
# Run tests (if test suite is implemented)
python -m pytest tests/
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `BLOCKCHAIN_DIFFICULTY`: Mining difficulty level

### Customization
- Modify `blockchain.py` for different consensus algorithms
- Update `models.py` for additional data fields
- Customize templates in `templates/` directory
- Adjust mining parameters in `app.py`

## 🚀 Deployment Guide

### 1. Set Environment Variables

Create a `.env` file or set these variables in your hosting environment:

```
SECRET_KEY=your-very-secret-key-here
DATABASE_URL=sqlite:///instance/voting_system.db  # Or your production database URI
```

### 2. Install Production Dependencies

```
pip install gunicorn  # For Linux
# or
pip install waitress  # For Windows
```

### 3. Run with a Production WSGI Server

**Linux (gunicorn):**
```
gunicorn -w 4 app:app
```

**Windows (waitress):**
```
waitress-serve --port=8080 app:app
```

### 4. Security Best Practices
- Never use the default SECRET_KEY in production.
- Always use HTTPS in production.
- Protect your database file and credentials.
- Do not run with debug=True in production.
- Regularly back up your database.
- Monitor logs for suspicious activity.

### 5. Static Files
- Serve static files (CSS, JS, images) with your web server (nginx, Apache) for best performance.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code comments

## 🔮 Future Enhancements

- **Multi-node Blockchain**: Distributed network implementation
- **Smart Contracts**: Ethereum integration for advanced voting logic
- **Mobile App**: Native mobile application
- **Advanced Analytics**: Detailed voting statistics and trends
- **Internationalization**: Multi-language support
- **Advanced Security**: Biometric authentication and 2FA

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Blockchain Basics](https://bitcoin.org/bitcoin.pdf)
- [Cryptographic Hashing](https://en.wikipedia.org/wiki/Cryptographic_hash_function)
- [Web Security Best Practices](https://owasp.org/www-project-top-ten/)

---

**Note**: This is a demonstration system. For production use in real elections, additional security measures, legal compliance, and extensive testing would be required. 