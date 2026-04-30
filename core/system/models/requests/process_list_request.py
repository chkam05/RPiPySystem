from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from core.data_filter.list_data_request import ListDataRequest


@dataclass
class ProcessListRequest(ListDataRequest):

    # --------------------------------------------------------------------------------
    # FIELD-NAME CONSTANTS
    # --------------------------------------------------------------------------------

    # Inherited from ListDataRequest.

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    fields: List[str] = field(default_factory=lambda: ProcessListRequest.default_fields())

    # --------------------------------------------------------------------------------
    # SERIALIZATION
    # --------------------------------------------------------------------------------

    @classmethod
    def default_fields(cls) -> List[str]:
        return ['process_id', 'process_name', 'user_name']

    # --------------------------------------------------------------------------------
    # SWAGGER SCHEMATICS
    # --------------------------------------------------------------------------------

    # Inherited from ListDataRequest.
