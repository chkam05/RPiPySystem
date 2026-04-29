from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional

from core.data.public_data_model import PublicDataModel


@dataclass
class OSUserInfo(PublicDataModel):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    FIELD_USER_NAME: ClassVar[str] = 'user_name'
    FIELD_USER_ID: ClassVar[str] = 'user_id'
    FIELD_GROUP_ID: ClassVar[str] = 'group_id'
    FIELD_USER_INFO: ClassVar[str] = 'user_info'
    FIELD_HOME_DIRECTORY: ClassVar[str] = 'home_directory'
    FIELD_SHELL_PATH: ClassVar[str] = 'shell_path'
    FIELD_CAN_LOGIN: ClassVar[str] = 'can_login'

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    user_name: str
    user_id: int
    group_id: Optional[int] = None
    user_info: Optional[str] = None
    home_directory: Optional[str] = None
    shell_path: Optional[str] = None
    can_login: bool = False

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> OSUserInfo:
        return cls(
            user_name=d[cls.FIELD_USER_NAME],
            user_id=d[cls.FIELD_USER_ID],
            group_id=d.get(cls.FIELD_GROUP_ID),
            user_info=d.get(cls.FIELD_USER_INFO),
            home_directory=d.get(cls.FIELD_HOME_DIRECTORY),
            shell_path=d.get(cls.FIELD_SHELL_PATH),
            can_login=bool(d.get(cls.FIELD_CAN_LOGIN, False)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_USER_NAME: self.user_name,
            self.FIELD_USER_ID: self.user_id,
            self.FIELD_GROUP_ID: self.group_id,
            self.FIELD_USER_INFO: self.user_info,
            self.FIELD_HOME_DIRECTORY: self.home_directory,
            self.FIELD_SHELL_PATH: self.shell_path,
            self.FIELD_CAN_LOGIN: self.can_login,
        }

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_USER_NAME: {'type': 'string', 'example': 'pi', 'description': 'System login name.'},
                cls.FIELD_USER_ID: {'type': 'integer', 'example': 1000, 'description': 'System user ID.'},
                cls.FIELD_GROUP_ID: {'type': 'integer', 'nullable': True, 'example': 1000, 'description': 'Primary group ID.'},
                cls.FIELD_USER_INFO: {'type': 'string', 'nullable': True, 'example': 'Raspberry Pi User', 'description': 'GECOS user information.'},
                cls.FIELD_HOME_DIRECTORY: {'type': 'string', 'nullable': True, 'example': '/home/pi', 'description': 'User home directory.'},
                cls.FIELD_SHELL_PATH: {'type': 'string', 'nullable': True, 'example': '/bin/bash', 'description': 'Configured login shell.'},
                cls.FIELD_CAN_LOGIN: {'type': 'boolean', 'example': True, 'description': 'Whether the account appears to be usable for interactive login.'},
            },
            'required': [cls.FIELD_USER_NAME, cls.FIELD_USER_ID, cls.FIELD_CAN_LOGIN],
        }
