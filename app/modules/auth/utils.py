"""Authentication utility functions for password hashing and JWT management."""

import hashlib
import uuid
import bcrypt
from datetime import datetime, timedelta

from jose import JWTError, jwt, ExpiredSignatureError

from app.core.config import settings
from app.modules.auth.exceptions import InvalidToken, TokenExpired


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_jti(jti: str) -> str:
    """Hash a JWT ID for storage in the database."""
    return hashlib.sha256(jti.encode()).hexdigest()


def create_access_token(user_id: int, email: str) -> str:
    """Create a new access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> tuple[str, str]:
    """Create a new refresh token and return (token, jti)."""
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": jti,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def verify_token(token: str, expected_type: str) -> dict:
    """Verify and decode a JWT token, raising specific exceptions on failure."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        if payload.get("type") != expected_type:
            raise InvalidToken()
        return payload

    except ExpiredSignatureError:
        raise TokenExpired()
    except JWTError:
        raise InvalidToken()