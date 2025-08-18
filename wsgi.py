#!/usr/bin/env python3
"""
Production WSGI entry point for the Blockchain Voting System
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set production environment
os.environ['FLASK_ENV'] = 'production'

# Import the app factory
from app_factory import create_app

# Create the application instance
application = create_app()

if __name__ == '__main__':
    # This should not be used in production
    # Use gunicorn or uwsgi instead
    print("WARNING: Running in development mode!")
    print("For production, use: gunicorn wsgi:application")
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
