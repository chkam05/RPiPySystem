from __future__ import annotations
from typing import List

from core.data_filter.list_data_filter import ListDataFilter
from core.system.models.process_info import ProcessInfo
from core.system.models.requests.process_list_request import ProcessListRequest


class ProcessesFilter(ListDataFilter):

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    available_fields: list[str] = list(ProcessInfo().to_dict().keys())
    default_fields: list[str] = ProcessListRequest().fields
