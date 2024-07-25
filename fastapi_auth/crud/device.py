from qrcode.image.svg import SvgImage
from sqlalchemy.orm import Session

from fastapi_auth.core.enums import DeviceTypeEnum
from fastapi_auth.core.two_factor_auth import create_encoded_two_factor_auth_key
from fastapi_auth.core.two_factor_auth import get_fake_otp_tokens
from fastapi_auth.core.two_factor_auth import qr_code_from_key
from fastapi_auth.crud.base_crud import CrudBase
from fastapi_auth.models.device import BackupToken
from fastapi_auth.models.device import Device
from fastapi_auth.models.users import User
from fastapi_auth.schemas.backup_token_schema import BackupTokenCreate
from fastapi_auth.schemas.device_schema import DeviceCreate
from fastapi_auth.schemas.device_schema import DeviceUpdate


class DeviceCrud(CrudBase[Device, DeviceCreate, DeviceUpdate]):
    """Database device information interaction interface"""

    # pylint: disable = arguments-differ
    async def create(self, db: Session, device: DeviceCreate, user: User) -> tuple[Device, SvgImage | None]:
        """Create a new device in the database"""
        # create device
        encoded_key: str = create_encoded_two_factor_auth_key()
        db_device = Device(key=encoded_key, user=user, device_type=device.device_type)
        # create backup tokens
        for token in get_fake_otp_tokens():
            backup_token_schema = BackupTokenCreate(token=token, device_id=db_device.id)
            token_db = BackupToken(**backup_token_schema.dict())
            db_device.backup_tokens.append(token_db)

        # avoid sqlachemy error  'obj already attached to session...'
        device_merged_session = await db.merge(db_device)
        db.add(device_merged_session)
        if await self.handle_commit(db):
            await db.refresh(db_device)

        # generate qr_code
        qr_code = None
        if device.device_type == DeviceTypeEnum.CODE_GENERATOR:
            qr_code = qr_code_from_key(encoded_key=encoded_key, user_email=user.email)
        return db_device, qr_code


device_crud = DeviceCrud(model=Device)
