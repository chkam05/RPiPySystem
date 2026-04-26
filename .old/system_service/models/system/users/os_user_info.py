from __future__ import annotations
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='OSUserInfo')


@dataclass
class OSUserInfo(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_USER_NAME: ClassVar[str] = 'user_name'
    FIELD_USER_ID: ClassVar[str] = 'user_id'
    FIELD_GROUP_ID: ClassVar[str] = 'group_id'
    FIELD_USER_INFO: ClassVar[str] = 'user_info'
    FIELD_HOME_DIRECTORY: ClassVar[str] = 'home_directory'
    FIELD_SHELL_PATH: ClassVar[str] = 'shell_path'
    FIELD_CAN_LOGIN: ClassVar[str] = 'can_login'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    user_name: str                  # login
    user_id: int                    # uid
    group_id: Optional[int]         # gid
    user_info: Optional[str]        # gecos
    home_directory: Optional[str]   # home
    shell_path: Optional[str]       # shell
    can_login: bool                 # computed from uid/shell

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> OSUserInfo:
        return cls(
            user_name=d.get(cls.FIELD_USER_NAME),
            user_id=d.get(cls.FIELD_USER_ID),
            group_id=d.get(cls.FIELD_GROUP_ID),
            user_info=d.get(cls.FIELD_USER_INFO),
            home_directory=d.get(cls.FIELD_HOME_DIRECTORY),
            shell_path=d.get(cls.FIELD_SHELL_PATH),
            can_login=d.get(cls.FIELD_CAN_LOGIN)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_USER_NAME: self.user_name,
            self.FIELD_USER_ID: self.user_id,
            self.FIELD_GROUP_ID: self.group_id,
            self.FIELD_USER_INFO: self.user_info,
            self.FIELD_HOME_DIRECTORY: self.home_directory,
            self.FIELD_SHELL_PATH: self.shell_path,
            self.FIELD_CAN_LOGIN: self.can_login
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_USER_NAME: {'type': 'string', 'example': 'root'},
                cls.FIELD_USER_ID: {'type': 'integer', 'example': 0},
                cls.FIELD_GROUP_ID: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_USER_INFO: {'type': ['string', 'null'], 'example': 'root'},
                cls.FIELD_HOME_DIRECTORY: {'type': ['string', 'null'], 'example': '/root'},
                cls.FIELD_SHELL_PATH: {'type': ['string', 'null'], 'example': '/bin/bash'},
                cls.FIELD_SHELL_PATH: {'type': 'boolean', 'example': True},
            },
            'required': [cls.FIELD_USER_NAME, cls.FIELD_USER_ID, cls.FIELD_SHELL_PATH],
            'additionalProperties': False,
        }