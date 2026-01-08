#!/usr/bin/env python3
"""
Test script to verify all services are working before deployment
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("=" * 60)
    print("TEST 1: Testing Imports")
    print("=" * 60)
    
    try:
        from flask import Flask
        print("[OK] Flask imported successfully")
    except ImportError as e:
        print(f"[FAIL] Flask import failed: {e}")
        return False
    
    try:
        from models import db, Voter, Election, Candidate, Vote
        print("[OK] Models imported successfully")
    except ImportError as e:
        print(f"[FAIL] Models import failed: {e}")
        return False
    
    try:
        from blockchain import Blockchain
        print("[OK] Blockchain imported successfully")
    except ImportError as e:
        print(f"[FAIL] Blockchain import failed: {e}")
        return False
    
    try:
        from app_factory import create_app
        print("[OK] App factory imported successfully")
    except ImportError as e:
        print(f"[FAIL] App factory import failed: {e}")
        return False
    
    try:
        # Set environment variables for testing
        import os
        if not os.environ.get('DATABASE_URL'):
            os.environ['DATABASE_URL'] = 'sqlite:///instance/test_voting_system.db'
        if not os.environ.get('FLASK_ENV'):
            os.environ['FLASK_ENV'] = 'development'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
        
        from wsgi import application
        print("[OK] WSGI application imported successfully")
    except ImportError as e:
        print(f"[FAIL] WSGI import failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] WSGI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\n" + "=" * 60)
    print("TEST 2: Testing App Creation")
    print("=" * 60)
    
    try:
        # Set environment variables for testing
        import os
        if not os.environ.get('DATABASE_URL'):
            os.environ['DATABASE_URL'] = 'sqlite:///instance/test_voting_system.db'
        if not os.environ.get('FLASK_ENV'):
            os.environ['FLASK_ENV'] = 'development'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'test-secret-key-for-testing-only'
        
        from app_factory import create_app
        app = create_app()
        print("[OK] Flask app created successfully")
        print(f"[OK] App name: {app.name}")
        print(f"[OK] Debug mode: {app.debug}")
        return True, app
    except Exception as e:
        print(f"[FAIL] App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_database_connection(app):
    """Test database connection"""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Database Connection")
    print("=" * 60)
    
    if not app:
        print("[FAIL] Cannot test database - app not created")
        return False
    
    try:
        with app.app_context():
            # Test database connection
            db.engine.connect()
            print("[OK] Database connection successful")
            
            # Test if tables exist
            from models import Voter, Election, Candidate, Vote
            print("[OK] Database models accessible")
            
            # Try to query
            voter_count = Voter.query.count()
            print(f"[OK] Database query successful (Voters: {voter_count})")
            
            return True
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_blockchain():
    """Test blockchain functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Blockchain")
    print("=" * 60)
    
    try:
        from blockchain import Blockchain
        blockchain = Blockchain()
        print("[OK] Blockchain created successfully")
        print(f"[OK] Chain length: {len(blockchain.chain)}")
        print(f"[OK] Genesis block hash: {blockchain.chain[0].hash[:20]}...")
        
        # Test chain validity
        is_valid = blockchain.is_chain_valid()
        print(f"[OK] Chain validity: {is_valid}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Blockchain test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes(app):
    """Test if routes are registered"""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Routes")
    print("=" * 60)
    
    if not app:
        print("[FAIL] Cannot test routes - app not created")
        return False
    
    required_routes = [
        '/',
        '/health',
        '/ping',
        '/login',
        '/register',
        '/elections',
        '/admin/elections'
    ]
    
    missing_routes = []
    for route in required_routes:
        # Check if route exists (simplified check)
        try:
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            if any(route in str(rule) for rule in app.url_map.iter_rules()):
                print(f"[OK] Route {route} is registered")
            else:
                missing_routes.append(route)
                print(f"[WARN] Route {route} not found")
        except Exception as e:
            print(f"[WARN] Could not check route {route}: {e}")
    
    if missing_routes:
        print(f"\n[WARN] Missing routes: {missing_routes}")
        return False
    
    return True

def test_health_endpoint(app):
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("TEST 6: Testing Health Endpoint")
    print("=" * 60)
    
    if not app:
        print("[FAIL] Cannot test health endpoint - app not created")
        return False
    
    try:
        with app.test_client() as client:
            response = client.get('/health')
            print(f"[OK] Health endpoint responded with status: {response.status_code}")
            if response.status_code == 200:
                print(f"[OK] Response: {response.get_json()}")
                return True
            else:
                print(f"[WARN] Unexpected status code: {response.status_code}")
                return False
    except Exception as e:
        print(f"[FAIL] Health endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wsgi():
    """Test WSGI application"""
    print("\n" + "=" * 60)
    print("TEST 7: Testing WSGI Application")
    print("=" * 60)
    
    try:
        from wsgi import application
        
        # Check if it's callable (WSGI requirement)
        if callable(application):
            print("[OK] WSGI application is callable")
        else:
            print("[FAIL] WSGI application is not callable")
            return False
        
        # Test if it has required attributes
        if hasattr(application, 'config'):
            print("[OK] WSGI application has config")
        else:
            print("[WARN] WSGI application missing config attribute")
        
        return True
    except Exception as e:
        print(f"[FAIL] WSGI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BLOCKCHAIN VOTING SYSTEM - PRE-DEPLOYMENT TESTS")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: App Creation
    app_created, app = test_app_creation()
    results.append(("App Creation", app_created))
    
    # Test 3: Database
    if app_created:
        results.append(("Database", test_database_connection(app)))
    
    # Test 4: Blockchain
    results.append(("Blockchain", test_blockchain()))
    
    # Test 5: Routes
    if app_created:
        results.append(("Routes", test_routes(app)))
    
    # Test 6: Health Endpoint
    if app_created:
        results.append(("Health Endpoint", test_health_endpoint(app)))
    
    # Test 7: WSGI
    results.append(("WSGI", test_wsgi()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Total: {len(results)} tests | Passed: {passed} | Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed! Your application is ready for deployment.")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please fix the issues before deploying.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
