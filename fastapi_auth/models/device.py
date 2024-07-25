from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from fastapi_auth.core import enums
from fastapi_auth.db.base_class import Base


class Device(Base):
    """A class for storing and recording all the device information relevant to the user"""

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    device_type = Column(postgresql.ENUM(enums.DeviceTypeEnum), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="device", uselist=False, lazy="joined")
    backup_tokens = relationship(
        "BackupToken",
        back_populates="device",
        uselist=True,
    )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}("
            f"id={self.id}, "
            f"device_type={self.device_type}, "
            f"user={self.user.full_name}, "
            f")>"
        )


class BackupToken(Base):
    """A class for storing backup token information"""

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("device.id"))
    device = relationship("Device", back_populates="backup_tokens", uselist=False)
    token = Column(String(length=8))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(" f"id={self.id}, " f"token={self.token}, " f"device={self.device}, " f")>"
