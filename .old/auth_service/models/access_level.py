from enum import Enum
from typing import List

from utils.base_str_enum import BaseStrEnum


class AccessLevel(BaseStrEnum):
    USER = 'user'
    ADMIN = 'admin'
    ROOT = 'root'