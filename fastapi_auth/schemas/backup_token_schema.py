from typing import Optional

from pydantic import BaseModel


# Shared properties
class BackupTokenBase(BaseModel):
    """Backup token information storage base class"""

    token: str


# Properties to receive via API on creation
class BackupTokenCreate(BackupTokenBase):
    """Backup token creation information class"""

    device_id: Optional[int]


# Properties to receive via API on update
class BackupTokenUpdate(BackupTokenBase):
    """Backup token update information class"""


class BackupTokenInDBBase(BackupTokenBase):
    """Backup token database storage class"""

    id: Optional[int] = None

    class Config:
        """Backup token configuration class"""

        orm_mode = True


class BackupTokenInDb(BackupTokenInDBBase):
    """Backup token additional parameter storage class"""


class BackupTokenOut(BackupTokenInDb):
    """Backup token output information class"""
