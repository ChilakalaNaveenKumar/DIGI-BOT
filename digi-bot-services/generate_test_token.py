#!/usr/bin/env python3
"""
Generate Test Token for API Testing
Creates a valid JWT token for testing API endpoints
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.auth.service.auth_service import AuthService


class DummyDB:
    """Dummy database session for token generation"""
    pass


def generate_test_token():
    """Generate a test JWT token"""
    
    # Create auth service with dummy DB
    auth_service = AuthService(DummyDB())
    
    # Test user data
    test_user_data = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "sub": "test_user_123",  # JWT standard claim
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    try:
        # Generate token
        token = auth_service.create_access_token(
            test_user_data,
            expires_delta=timedelta(hours=24)
        )
        
        print("Test Token Generated Successfully!")
        print("=" * 60)
        print(f"Token: {token}")
        print("=" * 60)
        print(f"User ID: {test_user_data['user_id']}")
        print(f"Email: {test_user_data['email']}")
        print(f"Name: {test_user_data['name']}")
        print(f"Expires: {test_user_data['exp']}")
        print("=" * 60)
        print("Copy this token to use in your API tests:")
        print(f'HEADERS = {{"Authorization": "Bearer {token}"}}')
        
        return token
        
    except Exception as e:
        print(f"Error generating token: {e}")
        return None


if __name__ == "__main__":
    generate_test_token()
