from typing import Any

from fastapi import APIRouter
from fastapi import Body
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_auth.api.deps.db import get_db
from fastapi_auth.api.deps.users import User
from fastapi_auth.api.deps.users import get_authenticated_user
from fastapi_auth.core import security
from fastapi_auth.core.config import settings
from fastapi_auth.core.enums import DeviceTypeEnum
from fastapi_auth.core.two_factor_auth import send_tfa_token
from fastapi_auth.core.utils import send_mail_backup_tokens
from fastapi_auth.crud.device import device_crud
from fastapi_auth.crud.users import user_crud
from fastapi_auth.schemas.jwt_token_schema import JwtTokenPayload
from fastapi_auth.schemas.jwt_token_schema import JwtTokenSchema
from fastapi_auth.schemas.jwt_token_schema import PreTfaJwtTokenSchema
from fastapi_auth.schemas.user_schema import UserCreate
from fastapi_auth.schemas.user_schema import UserOut

auth_router = APIRouter()


@auth_router.post(
    "/signup",
    summary="Create user",
    responses={
        200: {
            "content": {"image/jpg": {}},
            "description": "Returns no content or a qr code "
            "if tfas is enabled and device_type "
            "is 'code_generator'",
        }
    },
)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)) -> Any:
    """A routing function to create a new user and store his data in a database"""
    try:
        user = await user_crud(transaction=True).create(
            db=db,
            user=user_data,
        )
        if user_data.tfa_enabled:
            device, qr_code = await device_crud(transaction=True).create(db=db, device=user_data.device, user=user)
            send_mail_backup_tokens(user=user, device=device)

            if device.device_type == DeviceTypeEnum.CODE_GENERATOR:
                return StreamingResponse(content=qr_code, media_type="image/jpg")

        return Response(status_code=status.HTTP_200_OK)

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email `{user_data.email}` already exists",
        )
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex),
        )


@auth_router.post(
    "/login",
    summary="Create access and refresh tokens for user",
    status_code=status.HTTP_200_OK,
    response_model=JwtTokenSchema | PreTfaJwtTokenSchema,
    responses={
        200: {
            "description": "Credentials ok and TFA disabled",
        },
        202: {
            "description": "Credentials ok and TFA enabled",
        },
        401: {
            "description": "Invalid credentials",
        },
    },
)
async def login(
    response: Response,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """A routing function to allow user to get his data using his login and password"""
    user = await user_crud.authenticate(db=db, email=form_data.username, password=form_data.password)

    # wrong credentials
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # handle users with tfa enabled
    if user.tfa_enabled:
        send_tfa_token(user=user, device_type=user.device.device_type)
        response.status_code = status.HTTP_202_ACCEPTED
        return PreTfaJwtTokenSchema(
            access_token=security.create_pre_tfa_token(user.id),
            refresh_token=None,
        )

    # create access and refresh tokens
    return JwtTokenSchema(
        access_token=security.create_jwt_access_token(user.id),
        refresh_token=security.create_jwt_refresh_token(user.id),
    )


@auth_router.get("/test-token", summary="Authenticated endpoint to test if access token is ok", response_model=UserOut)
async def test_token(user: User = Depends(get_authenticated_user)):
    """A routing function to test whether the user has a functional access token (doesn't always work in FastAPI)"""
    return user


@auth_router.post("/refresh", summary="Refresh token for elapsed access token", response_model=JwtTokenSchema)
async def refresh_token_task(
    db: Session = Depends(get_db), refresh_token: str = Body(embed=True, title="refresh token")
):
    """A routing function to refresh a user's access token"""
    try:
        payload = jwt.decode(
            token=refresh_token,
            key=settings.JWT_SECRET_KEY_REFRESH,
            algorithms=[settings.ALGORITHM],
        )
        token_data = JwtTokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await user_crud.get(db, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token for user",
        )
    return {
        "access_token": security.create_jwt_access_token(user.id),
        "refresh_token": security.create_jwt_refresh_token(user.id),
    }
