"""Authentication dependencies for protected API endpoints."""

import logging

from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth import utils
from app.modules.auth import service
from app.modules.auth.models import User
from app.modules.auth.exceptions import InvalidToken, TokenExpired, AuthenticationError

logger = logging.getLogger(__name__)

# Defines the security scheme to be used in the API docs and for token extraction.
http_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current user from a JWT access token.

    Verifies the token and fetches the corresponding user from the database.
    Raises a specific AuthenticationError for any authentication failure.
    """
    if credentials is None:
        logger.warning("Authentication failed: No credentials provided.")
        raise AuthenticationError(message="Not authenticated")

    token = credentials.credentials
    try:
        payload = utils.verify_token(token, expected_type="access")
        user_id = int(payload.get("sub"))
        if user_id is None:
            logger.warning("Token validation failed: user_id (sub) is missing.")
            raise AuthenticationError(message="Invalid token: sub claim missing")
            
    except TokenExpired:
        logger.warning("Token validation failed: token has expired.")
        raise AuthenticationError(message="Token has expired")
        
    except (InvalidToken, ValueError, TypeError):
        logger.warning("Token validation failed: token is invalid or malformed.")
        raise AuthenticationError(message="Invalid token")

    user = service.get_user_by_id(db=db, user_id=user_id)
    if user is None:
        logger.warning(f"Token validation failed: user_id {user_id} not found in DB.")
        raise AuthenticationError(message="Invalid token")

    return user