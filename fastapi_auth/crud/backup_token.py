from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from fastapi_auth.crud.base_crud import CrudBase
from fastapi_auth.models.device import BackupToken
from fastapi_auth.models.device import Device
from fastapi_auth.models.users import User
from fastapi_auth.schemas.backup_token_schema import BackupTokenCreate
from fastapi_auth.schemas.backup_token_schema import BackupTokenUpdate


class BackupTokenCrud(CrudBase[Device, BackupTokenCreate, BackupTokenUpdate]):
    """A class for fetching user's backup tokens"""

    @staticmethod
    async def get_user_backup_tokens(db: Session, user: User) -> list:
        """Fetch user's backup tokens from the database"""
        if not user.device:
            return []
        result = await db.execute(
            select(Device).where(Device.id == user.device.id).options(joinedload(Device.backup_tokens))
        )
        device_with_bkp_tokens: Device = result.scalar()
        return device_with_bkp_tokens.backup_tokens


backup_token_crud = BackupTokenCrud(model=BackupToken)
