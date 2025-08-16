#!/usr/bin/env python3
"""
Deployment helper script for Render
"""
import os
import subprocess
import sys

def check_git_status():
    """Check if git repository is clean"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        if result.stdout.strip():
            print("⚠️  Warning: You have uncommitted changes:")
            print(result.stdout)
            response = input("Do you want to continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Deployment cancelled. Please commit your changes first.")
                sys.exit(1)
        else:
            print("✅ Git repository is clean")
    except subprocess.CalledProcessError:
        print("❌ Error checking git status")
        sys.exit(1)

def check_files():
    """Check if all required files exist"""
    required_files = [
        'render.yaml',
        'wsgi.py',
        'app_factory.py',
        'routes.py',
        'config.py',
        'requirements-prod.txt',
        'gunicorn.conf.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all required files are present before deploying.")
        sys.exit(1)
    else:
        print("✅ All required files are present")

def show_deployment_steps():
    """Show deployment steps"""
    print("\n🚀 Render Deployment Steps:")
    print("=" * 50)
    print("1. Go to [render.com](https://render.com)")
    print("2. Click 'Get Started for Free'")
    print("3. Sign up with GitHub (recommended)")
    print("4. Click 'New +' → 'Blueprint'")
    print("5. Connect your GitHub repository")
    print("6. Select: Sudo-Kartik2005/-name-blockchain-voting-system")
    print("7. Click 'Apply'")
    print("8. Wait for deployment to complete")
    print("9. Check the health endpoint: /health")
    print("\n📋 Your app will be available at:")
    print("   https://your-app-name.onrender.com")

def show_environment_variables():
    """Show required environment variables"""
    print("\n🔧 Environment Variables (Auto-configured by Render):")
    print("=" * 50)
    print("✅ FLASK_ENV=production")
    print("✅ SECRET_KEY (auto-generated)")
    print("✅ DATABASE_URL (auto-configured)")
    print("✅ PYTHON_VERSION=3.12.0")
    print("✅ LOG_LEVEL=INFO")
    print("✅ BLOCKCHAIN_MINING_INTERVAL=10")

def show_testing_commands():
    """Show testing commands"""
    print("\n🧪 Test Your Deployment:")
    print("=" * 50)
    print("1. Health Check: /health")
    print("2. Basic Route: /ping")
    print("3. Debug Info: /debug")
    print("4. Main Page: /")
    print("\n📊 Monitor in Render Dashboard:")
    print("   - Build logs")
    print("   - Health status")
    print("   - Database usage")

def main():
    """Main deployment helper"""
    print("🚀 Render Deployment Helper for Blockchain Voting System")
    print("=" * 60)
    
    # Check prerequisites
    check_git_status()
    check_files()
    
    # Show deployment information
    show_deployment_steps()
    show_environment_variables()
    show_testing_commands()
    
    print("\n🎉 Ready to deploy!")
    print("Push your changes to GitHub and Render will auto-deploy:")
    print("\n   git add .")
    print("   git commit -m 'Ready for Render deployment'")
    print("   git push origin main")
    
    print("\n📚 For more details, see: RENDER_DEPLOYMENT.md")

if __name__ == '__main__':
    main()
