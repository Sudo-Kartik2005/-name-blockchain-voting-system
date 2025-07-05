#!/usr/bin/env python3
"""
Setup script for Blockchain Voting System
This script helps set up the environment and install dependencies
"""

import subprocess
import sys
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_pip():
    """Install pip if not available"""
    try:
        import pip
        print("✅ pip is already installed")
        return True
    except ImportError:
        print("📦 Installing pip...")
        try:
            # Download get-pip.py
            import urllib.request
            url = "https://bootstrap.pypa.io/get-pip.py"
            urllib.request.urlretrieve(url, "get-pip.py")
            
            # Install pip
            subprocess.check_call([sys.executable, "get-pip.py"])
            
            # Clean up
            os.remove("get-pip.py")
            print("✅ pip installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install pip: {e}")
            print("   Please install pip manually: https://pip.pypa.io/en/stable/installation/")
            return False

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    dependencies = [
        "Flask==2.3.3",
        "Flask-SQLAlchemy==3.0.5", 
        "Flask-Login==0.6.3",
        "Flask-WTF==1.1.1",
        "WTForms==3.0.1",
        "cryptography==41.0.7"
    ]
    
    for dep in dependencies:
        try:
            print(f"   Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ All dependencies installed successfully")
    return True

def create_virtual_environment():
    """Create a virtual environment"""
    print("🔧 Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created")
        print("\n📋 To activate the virtual environment:")
        if os.name == 'nt':  # Windows
            print("   venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("   source venv/bin/activate")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Blockchain Voting System Setup\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install pip if needed
    if not install_pip():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create virtual environment
    create_virtual_environment()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Activate the virtual environment")
    print("   2. Run: python test_system.py")
    print("   3. Start the application: python app.py")
    print("   4. Visit: http://localhost:5000")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main() 