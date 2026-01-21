"""Authentication API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth import service
from app.modules.auth import utils
from app.modules.auth.schemas import (
    SignUpRequest,
    SignUpResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse
)
from app.modules.auth.exceptions import UserAlreadyExists, InvalidCredentials, InvalidToken
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=SignUpResponse, status_code=201)
def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(f"Processing signup for email: {request.email}")
    try:
        service.create_user(db, request.name, request.email, request.password)
        return SignUpResponse(message="User created successfully. Please log in.")
    except AppException as e:
        logger.error(f"Signup failed for email {request.email}: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return tokens."""
    logger.info(f"Processing login for email: {request.email}")
    try:
        # Authenticate user
        user = service.authenticate_user(db, request.email, request.password)
        
        # Generate tokens
        access_token = utils.create_access_token(user.id, user.email)
        refresh_token, jti = utils.create_refresh_token(user.id)
        
        # Update refresh token JTI hash
        service.update_refresh_token(db, user, jti)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except AppException as e:
        logger.error(f"Login failed for email {request.email}: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    logger.info("Processing token refresh request.")
    try:
        # Verify refresh token and get user
        user = service.verify_refresh_token(db, request.refresh_token)
        
        # Generate new tokens (rotation)
        access_token = utils.create_access_token(user.id, user.email)
        refresh_token, jti = utils.create_refresh_token(user.id)
        
        # Update refresh token JTI hash (invalidates old token)
        service.update_refresh_token(db, user, jti)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except AppException as e:
        logger.error(f"Token refresh failed: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
