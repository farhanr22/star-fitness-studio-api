"""Authentication service with user management business logic."""

from sqlalchemy.orm import Session

from app.modules.auth import utils
from app.modules.auth.models import User
from app.modules.auth.exceptions import InvalidCredentials, UserAlreadyExists, InvalidToken


def create_user(db: Session, name: str, email: str, password: str) -> User:
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise UserAlreadyExists()
    
    # Create new user
    user = User(
        name=name,
        email=email,
        password_hash=utils.hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate a user by email and password."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not utils.verify_password(password, user.password_hash):
        raise InvalidCredentials()
    
    return user


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Fetch a user by their unique ID."""
    return db.query(User).filter(User.id == user_id).first()


def update_refresh_token(db: Session, user: User, jti: str) -> None:
    """Update user's refresh token JTI hash."""
    user.refresh_token_jti_hash = utils.hash_jti(jti)
    db.commit()


def verify_refresh_token(db: Session, token: str) -> User:
    """Verify refresh token and return associated user."""
    payload = utils.verify_token(token, "refresh")
    
    user_id = int(payload["sub"])
    jti = payload["jti"]
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise InvalidToken()
    
    # Verify JTI hash matches the one stored for the user
    if user.refresh_token_jti_hash != utils.hash_jti(jti):
        raise InvalidToken()
    
    return user