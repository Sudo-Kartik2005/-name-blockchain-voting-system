#!/usr/bin/env python3
"""
Development script to run the voting system with email disabled
"""
import os
import sys

# Set environment variables for development
os.environ['MAIL_DISABLED'] = 'true'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Import and run the app
from app import app

if __name__ == '__main__':
    print("Starting development server with email disabled...")
    print("OTP codes will be displayed in flash messages instead of being sent via email.")
    print("Access the application at: http://127.0.0.1:8080")
    print("Press Ctrl+C to stop the server.")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=8080) 