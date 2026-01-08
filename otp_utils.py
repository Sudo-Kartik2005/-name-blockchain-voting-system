#!/usr/bin/env python3
"""
OTP (One-Time Password) utility functions for authentication
"""
import random
import string
from datetime import datetime, timedelta
from models import db, OTPCode, Voter
import secrets

def generate_otp(length=6):
    """
    Generate a random OTP code
    
    Args:
        length: Length of OTP code (default: 6)
    
    Returns:
        str: Random OTP code
    """
    # Generate numeric OTP for easier entry
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def create_otp(voter_id, purpose='login', expiry_minutes=10, ip_address=None):
    """
    Create and store an OTP code in the database
    
    Args:
        voter_id: ID of the voter
        purpose: Purpose of OTP ('login', 'password_reset', etc.)
        expiry_minutes: Minutes until OTP expires (default: 10)
        ip_address: IP address of the requester
    
    Returns:
        OTPCode: The created OTP code object
    """
    # Invalidate any existing unused OTPs for this voter and purpose
    existing_otps = OTPCode.query.filter_by(
        voter_id=voter_id,
        purpose=purpose,
        is_used=False
    ).all()
    
    for otp in existing_otps:
        otp.is_used = True  # Mark as used/invalid
    
    # Generate new OTP
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    
    otp = OTPCode(
        voter_id=voter_id,
        code=code,
        purpose=purpose,
        expires_at=expires_at,
        ip_address=ip_address
    )
    
    db.session.add(otp)
    db.session.commit()
    
    return otp

def verify_otp(voter_id, code, purpose='login', ip_address=None):
    """
    Verify an OTP code
    
    Args:
        voter_id: ID of the voter
        code: OTP code to verify
        purpose: Purpose of OTP
        ip_address: IP address (optional, for logging)
    
    Returns:
        tuple: (success: bool, message: str, otp_object: OTPCode or None)
    """
    # Find the most recent unused OTP for this voter and purpose
    otp = OTPCode.query.filter_by(
        voter_id=voter_id,
        purpose=purpose,
        is_used=False
    ).order_by(OTPCode.created_at.desc()).first()
    
    if not otp:
        return False, "No valid OTP found. Please request a new one.", None
    
    if not otp.is_valid():
        return False, "OTP has expired. Please request a new one.", None
    
    if otp.code != code:
        return False, "Invalid OTP code. Please try again.", None
    
    # Optional: Verify IP address matches (for additional security)
    if ip_address and otp.ip_address and otp.ip_address != ip_address:
        # Log this as suspicious activity but don't block (IP might change)
        pass
    
    # Mark OTP as used
    otp.is_used = True
    db.session.commit()
    
    return True, "OTP verified successfully.", otp

def send_otp_email(voter, otp_code):
    """
    Send OTP code via email
    
    Args:
        voter: Voter object
        otp_code: OTP code string
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        from flask import current_app
        from flask_mail import Message
        
        # Check if mail is disabled (for development)
        if current_app.config.get('MAIL_DISABLED', False):
            print(f"[DEV MODE] OTP for {voter.email}: {otp_code}")
            return True
        
        # Get mail configuration
        mail = current_app.extensions.get('mail')
        if not mail:
            print("Mail extension not initialized. OTP code:", otp_code)
            return False
        
        # Create email message
        msg = Message(
            subject='Your Login OTP Code',
            recipients=[voter.email],
            body=f"""
Hello {voter.first_name},

Your OTP code for login is: {otp_code}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Best regards,
Blockchain Voting System
            """,
            html=f"""
<html>
<body>
    <h2>Your Login OTP Code</h2>
    <p>Hello {voter.first_name},</p>
    <p>Your OTP code for login is: <strong style="font-size: 24px; color: #007bff;">{otp_code}</strong></p>
    <p>This code will expire in <strong>10 minutes</strong>.</p>
    <p>If you did not request this code, please ignore this email.</p>
    <hr>
    <p><small>Best regards,<br>Blockchain Voting System</small></p>
</body>
</html>
            """
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False

def cleanup_expired_otps():
    """
    Clean up expired OTP codes from the database
    This should be called periodically
    """
    expired_otps = OTPCode.query.filter(
        OTPCode.expires_at < datetime.utcnow()
    ).all()
    
    count = 0
    for otp in expired_otps:
        if not otp.is_used:
            otp.is_used = True  # Mark as used
            count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Cleaned up {count} expired OTP codes")
    
    return count

