#!/usr/bin/env python3
"""
Simple test to check login route
"""
import requests
import json

def test_login_route():
    """Test the login route directly"""
    base_url = "http://127.0.0.1:8080"
    
    print("=== Testing Login Route ===")
    
    try:
        # Test if the app is running
        response = requests.get(f"{base_url}/ping")
        if response.status_code == 200:
            print("✓ Application is running")
        else:
            print("✗ Application is not responding")
            return
        
        # Test login page
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✓ Login page is accessible")
        else:
            print("✗ Login page is not accessible")
            return
        
        # Test index page (should redirect to login if not authenticated)
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Index page is accessible")
        else:
            print("✗ Index page is not accessible")
            return
        
        print("\n=== Manual Testing Required ===")
        print("1. Open your browser and go to: http://127.0.0.1:8080")
        print("2. Try to login with:")
        print("   Username: admin")
        print("   Password: admin123")
        print("3. Check the console output for any errors")
        print("4. Check if you get redirected to login page after login")
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to application")
        print("Make sure the application is running with: python run_dev.py")
    except Exception as e:
        print(f"✗ Error testing login route: {e}")

if __name__ == '__main__':
    test_login_route()
