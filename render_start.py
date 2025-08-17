#!/usr/bin/env python3
"""
Render startup script for the Blockchain Voting System
"""
import os
import sys
import subprocess

def main():
    print("🚀 Starting Blockchain Voting System on Render...")
    
    # Check if gunicorn is available
    try:
        import gunicorn
        print("✅ Gunicorn is available")
    except ImportError:
        print("❌ Gunicorn not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "gunicorn"], check=True)
        print("✅ Gunicorn installed")
    
    # Get port from environment (Render sets this)
    port = os.environ.get('PORT', '8000')
    print(f"🌐 Binding to port: {port}")
    
    # Start gunicorn
    print("🚀 Starting gunicorn...")
    cmd = [
        sys.executable, "-m", "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--workers", "1",
        "--timeout", "30",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--log-level", "info",
        "wsgi:application"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    os.execv(sys.executable, [sys.executable, "-m", "gunicorn"] + cmd[2:])

if __name__ == "__main__":
    main()
