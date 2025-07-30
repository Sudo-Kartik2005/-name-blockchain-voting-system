# Blockchain Voting System - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

#### Option A: Development Mode (Recommended for testing)
```bash
python run_dev.py
```
This runs the application with email disabled. OTP codes will be displayed in flash messages.

#### Option B: Production Mode
```bash
python app.py
```
This runs the application with email enabled (requires Mailtrap credentials).

### 3. Create Admin User
```bash
python create_admin.py
```
This creates an admin user with credentials:
- Username: `newadmin`
- Password: `123456`

### 4. Access the Application
- Open your browser and go to: http://127.0.0.1:8080
- Register a new voter account or login as admin

## Common Issues and Solutions

### 1. Email Configuration Error
**Error**: `SMTPServerDisconnected: Connection unexpectedly closed`

**Solution**: 
- Use `python run_dev.py` for development (email disabled)
- Or set up Mailtrap credentials:
  ```bash
  export MAIL_USERNAME=your-mailtrap-username
  export MAIL_PASSWORD=your-mailtrap-password
  ```

### 2. Database Issues
**Error**: Database not found or tables missing

**Solution**: The database is automatically created when you run the application for the first time.

### 3. Port Already in Use
**Error**: Port 8080 already in use

**Solution**: 
- Change the port in `app.py` or `run_dev.py`
- Or kill the process using port 8080

### 4. Import Errors
**Error**: Module not found

**Solution**: 
- Make sure you're in the virtual environment
- Run `pip install -r requirements.txt`

### 5. Date Handling Error
**Error**: `SQLite Date type only accepts Python date objects as input`

**Solution**: 
- This has been fixed in the latest version
- The application now properly handles date fields in registration forms
- If you encounter this error, make sure you're using the latest code

## Features

### For Voters:
- Register with OTP verification
- View active elections
- Cast votes in elections
- View election results

### For Admins:
- Create and manage elections
- Add/edit/delete candidates
- View blockchain data
- Mine pending transactions
- Validate blockchain integrity

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-secret-key-change-this-in-production` |
| `DATABASE_URL` | Database connection string | SQLite file in instance/ |
| `MAIL_USERNAME` | Mailtrap username | `your-mailtrap-username` |
| `MAIL_PASSWORD` | Mailtrap password | `your-mailtrap-password` |
| `MAIL_DISABLED` | Disable email functionality | `false` |
| `PORT` | Application port | `8080` |

## Project Structure

```
vote/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── forms.py               # WTForms definitions
├── blockchain.py          # Blockchain implementation
├── run_dev.py            # Development server script
├── create_admin.py       # Admin user creation script
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
├── instance/             # Database files (auto-created)
└── README.md            # Project documentation
```

## Testing the System

1. **Register a new voter**:
   - Go to http://127.0.0.1:8080/register
   - Fill in the registration form
   - Use the OTP code displayed in the flash message

2. **Login as admin**:
   - Run `python create_admin.py`
   - Login with username: `newadmin`, password: `123456`

3. **Create an election**:
   - Go to Admin → Elections
   - Create a new election with start/end dates

4. **Add candidates**:
   - Go to the election → Manage Candidates
   - Add candidates to the election

5. **Cast votes**:
   - Login as a voter
   - Go to Elections → Select an election → Vote

6. **View results**:
   - Go to the election → View Results
   - Check both database and blockchain results

## Troubleshooting

### Application won't start
- Check if all dependencies are installed
- Ensure you're in the virtual environment
- Check if port 8080 is available

### Registration fails
- Check if email is properly configured
- Use development mode if email setup is problematic
- Check browser console for JavaScript errors

### Admin features not working
- Ensure you're logged in as an admin user
- Run `python create_admin.py` to create admin user
- Check if `is_admin` flag is set to `True`

### Blockchain issues
- Check the admin blockchain page for errors
- Try mining pending transactions manually
- Validate the blockchain integrity

## Support

If you encounter any issues:
1. Check this setup guide
2. Look at the application logs
3. Verify all dependencies are installed
4. Ensure database is properly initialized 