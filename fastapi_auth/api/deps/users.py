from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from fastapi_auth.api.deps.db import get_db
from fastapi_auth.core.config import settings
from fastapi_auth.core.two_factor_auth import verify_token
from fastapi_auth.crud.users import user_crud
from fastapi_auth.models.users import User
from fastapi_auth.schemas.jwt_token_schema import JwtTokenPayload

REUSABLE_OAUTH = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", scheme_name="JWT")


async def get_user_from_jwt(
    key: str,
    token: str,
    db: Session,
    expire_err_message: str = "Token expired",
    jwt_err_message: str = "Could not validate credentials, if TFA is enabled, please confirm token first",
):
    """Find a user by his JWT access token"""
    try:
        payload = jwt.decode(token=token, key=key, algorithms=[settings.ALGORITHM])
        token_data = JwtTokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=expire_err_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=jwt_err_message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_crud.get(db=db, id=token_data.sub)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user


async def get_authenticated_user(
    token: str = Depends(REUSABLE_OAUTH),
    db: Session = Depends(get_db),
) -> User:
    """Return authenticated user's info based on his JWT token"""
    return await get_user_from_jwt(key=settings.JWT_SECRET_KEY, token=token, db=db)


async def get_authenticated_user_pre_tfa(
    token: str = Depends(REUSABLE_OAUTH),
    db: Session = Depends(get_db),
) -> User:
    """Use a pre-TFA token to return authenticated user's information"""
    return await get_user_from_jwt(
        token=token,
        key=settings.PRE_TFA_SECRET_KEY,
        db=db,
        expire_err_message="Token expired, login again "
        "and validate TFA token within "
        f"{settings.PRE_TFA_TOKEN_EXPIRE_MINUTES} minutes",
    )


async def get_authenticated_tfa_user(tfa_token: str, user: User = Depends(get_authenticated_user_pre_tfa)) -> User:
    """Return authenticated user's info based on his JWT token (if he has TFA enabled)"""
    if verify_token(user=user, token=tfa_token):
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="TOTP token mismatch")
