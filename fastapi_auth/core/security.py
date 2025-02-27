from datetime import datetime
from datetime import timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from fastapi_auth.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Returns the hashed version of a string

    Args:
        password (str)

    Returns:
        str: hashed psw
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check password hash with given hashed value

    Args:
        password (str): raw password
        hashed_password (str): hashed version of raw password

    Returns:
        bool: True if passwords match hashed password
    """
    return pwd_context.verify(password, hashed_password)


def _create_token(
    subject: int | Any,
    expire_minutes: int,
    key: str,
) -> str:
    """Create a JWT token

    Args:
        subject (int | Any)
        expire_minutes (int)
        key (str): key to do the encoding/decoding

    Returns:
        str: encoded jwt
    """
    expires_delta = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {
        "sub": str(subject),
        "exp": expires_delta,
    }

    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=key,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def create_jwt_access_token(subject: int | Any) -> str:
    """Create a JWT access token"""
    return _create_token(
        subject=subject,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        key=settings.JWT_SECRET_KEY,
    )


def create_jwt_refresh_token(subject: int | Any) -> str:
    """Create a JWT refresh token"""
    return _create_token(
        subject=subject,
        expire_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        key=settings.JWT_SECRET_KEY_REFRESH,
    )


def create_pre_tfa_token(subject: int | Any) -> str:
    """Create a pre-TFA JWT token"""
    return _create_token(
        subject=subject,
        expire_minutes=settings.PRE_TFA_TOKEN_EXPIRE_MINUTES,
        key=settings.PRE_TFA_SECRET_KEY,
    )
