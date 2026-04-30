from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from core.data_filter.list_data_request import ListDataRequest


@dataclass
class UserListRequest(ListDataRequest):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    # Inherited from ListDataRequest.

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    fields: List[str] = field(default_factory=lambda: UserListRequest.default_fields())

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def default_fields(cls) -> List[str]:
        return ['user_id', 'user_name']

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    # Inherited from ListDataRequest.
