#!/usr/bin/env python3
"""
Render startup script for the Blockchain Voting System
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Render environment
os.environ['FLASK_ENV'] = 'production'

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main Render startup function"""
    try:
        # Import the app factory
        from app_factory import create_app
        
        # Create the application instance
        app = create_app()
        
        # Get port from Render environment
        port = int(os.environ.get('PORT', 10000))
        
        print(f"🚀 Starting Render server on port {port}")
        print("🌍 Environment: PRODUCTION")
        print("🔒 Debug mode: DISABLED")
        print("🗄️ Database: {database_type}".format(
            database_type="PostgreSQL" if "postgresql" in os.environ.get('DATABASE_URL', '') else "SQLite"
        ))
        print("🔑 Secret Key: {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}")
        print("🏗️ Platform: Render")
        
        # Run with Render settings
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements-prod.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
