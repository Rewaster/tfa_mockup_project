from typing import Optional

from pydantic import BaseModel

from fastapi_auth.core.enums import DeviceTypeEnum


# Shared properties
class DeviceBase(BaseModel):
    """Device type storage class"""

    device_type: DeviceTypeEnum


# Properties to receive via API on creation
class DeviceCreate(DeviceBase):
    """Device creation class"""


# Properties to receive via API on update
class DeviceUpdate(DeviceBase):
    """Device update information storage class"""


class DeviceInDBBase(DeviceBase):
    """Device database storage class"""

    id: Optional[int] = None

    class Config:
        """Configuration storage class for device database information"""

        orm_mode = True


class DeviceInDb(DeviceInDBBase):
    """Additional params storage for device database class"""

    key: str
