from typing import Optional

from fastapi import HTTPException
from fastapi import status
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import model_validator

from fastapi_auth.schemas.device_schema import DeviceCreate
from fastapi_auth.schemas.device_schema import DeviceInDBBase


# Shared properties
class UserBase(BaseModel):
    """User database information class"""

    email: EmailStr
    tfa_enabled: Optional[bool] = False
    full_name: str


class UserLogin(BaseModel):
    """User login information class"""

    email: EmailStr
    password: str


# Properties to receive via API on creation
class UserCreate(UserBase):
    """User creation class"""

    password: str
    device: Optional[DeviceCreate] = None

    @model_validator(mode="before")
    @classmethod
    def check_device_if_tfa_enabled(cls, values):
        """Checks if the user has TFA enabled"""
        if values["tfa_enabled"] and values["device"] is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "When enabling TFA, a device_type should also be provided",
            )
        return values


# Properties to receive via API on update
class UserUpdate(BaseModel):
    """User information update class"""

    email: Optional[EmailStr] = None
    tfa_enabled: Optional[bool] = False
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """User information database storage class"""

    id: Optional[int] = None
    device: Optional[DeviceInDBBase] = None

    class Config:
        """Configuration settings for user information class"""

        orm_mode = True


# Additional properties to return via API
class UserOut(UserInDBBase):
    """User information database return class"""


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    """User information database password storage class"""

    hashed_password: str
