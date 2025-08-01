#!/usr/bin/env python3
"""
Test script for email validator functionality
"""

import re

def test_simple_email_validator():
    """Test the simple email validator"""
    print("=== Testing Simple Email Validator ===")
    
    # Simple email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Test valid emails
    valid_emails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'user+tag@example.org',
        'user123@test-domain.com'
    ]
    
    # Test invalid emails
    invalid_emails = [
        'invalid-email',
        '@example.com',
        'user@',
        'user@.com',
        'user..name@example.com'
    ]
    
    print("Testing valid emails:")
    for email in valid_emails:
        is_valid = bool(re.match(pattern, email))
        print(f"  {email}: {'✓' if is_valid else '✗'}")
    
    print("\nTesting invalid emails:")
    for email in invalid_emails:
        is_valid = bool(re.match(pattern, email))
        print(f"  {email}: {'✓' if is_valid else '✗'}")
    
    print("\n✓ Email validator test completed")

if __name__ == "__main__":
    test_simple_email_validator() 