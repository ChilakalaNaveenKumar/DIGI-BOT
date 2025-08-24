# Authentication Service

This directory contains all authentication and authorization related services for the Digi Bot application.

## Structure

```
app/services/auth/
├── __init__.py                 # Module exports and documentation
├── core/                      # Core authentication components
│   ├── __init__.py
│   ├── auth_deps.py          # FastAPI authentication dependencies
│   └── security.py           # Security manager and token handling
├── service/                   # Authentication service implementations
│   ├── __init__.py
│   └── auth_service.py       # Core authentication service
├── router/                    # FastAPI routers for auth endpoints
│   ├── __init__.py
│   └── enhanced_auth_router.py # Authentication API routes
└── README.md                  # This documentation
```

## Components

### Core Components

#### SecurityManager (`core/security.py`)
Advanced security features including:
- CSRF token generation and validation
- Refresh token management
- One-time authentication codes
- Security event logging
- Token expiration handling

#### Authentication Dependencies (`core/auth_deps.py`)
FastAPI dependency functions for:
- Cookie-based authentication
- User session validation
- Required authentication enforcement
- Optional authentication support

### Service Components

#### AuthService (`service/auth_service.py`)
Core authentication service that handles:
- Password hashing and verification using bcrypt
- User authentication against the database
- JWT token creation and verification
- User session management

### Router Components

#### Enhanced Auth Router (`router/enhanced_auth_router.py`)
FastAPI router providing secure authentication endpoints:
- Google OAuth integration
- Token exchange endpoints
- Secure cookie management
- CSRF protection
- Session management

## Usage

```python
from app.services.auth import (
    AuthService,
    SecurityManager,
    security_manager,
    get_current_user_from_cookie,
    get_current_user_required,
    enhanced_auth_router
)

# Use in FastAPI app
app.include_router(enhanced_auth_router)

# Use as dependency
@app.get("/protected")
async def protected_route(
    user = Depends(get_current_user_required)
):
    return {"user": user}
```

## Security Features

- **HIPAA Compliant**: Secure token management and session handling
- **CSRF Protection**: Cross-site request forgery prevention
- **Secure Cookies**: HttpOnly, Secure, SameSite cookie attributes
- **Token Rotation**: Automatic refresh token rotation
- **Security Logging**: Comprehensive audit trail
- **Rate Limiting**: Built-in protection against brute force attacks

## Configuration

Authentication settings are managed through the main application configuration:
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth callback URL
