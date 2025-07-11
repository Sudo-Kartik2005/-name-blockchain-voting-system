#!/usr/bin/env python3
"""
Check if the edit routes are properly registered
"""

from app import app

def check_routes():
    """Check if the edit routes are registered"""
    print("🔍 Checking registered routes...")
    print("=" * 50)
    
    with app.app_context():
        # Get all registered routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        
        # Filter for candidate-related routes
        candidate_routes = [r for r in routes if 'candidate' in r['endpoint']]
        
        print("📋 Candidate-related routes:")
        for route in candidate_routes:
            print(f"  {route['endpoint']}: {route['rule']} [{', '.join(route['methods'])}]")
        
        # Check for specific edit route
        edit_routes = [r for r in routes if 'edit_candidate' in r['endpoint']]
        if edit_routes:
            print("\n✅ Edit candidate route found!")
            for route in edit_routes:
                print(f"  {route['rule']}")
        else:
            print("\n❌ Edit candidate route NOT found!")
        
        # Check for delete route
        delete_routes = [r for r in routes if 'delete_candidate' in r['endpoint']]
        if delete_routes:
            print("✅ Delete candidate route found!")
            for route in delete_routes:
                print(f"  {route['rule']}")
        else:
            print("❌ Delete candidate route NOT found!")

if __name__ == "__main__":
    check_routes() 