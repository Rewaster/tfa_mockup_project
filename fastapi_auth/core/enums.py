from enum import Enum


class DeviceTypeEnum(str, Enum):
    """Device type storage class"""

    EMAIL: str = "email"
    CODE_GENERATOR: str = "code_generator"

    def __str__(self):
        return self.value
