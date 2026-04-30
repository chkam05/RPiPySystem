from __future__ import annotations
from typing import List

from core.data_filter.list_data_filter import ListDataFilter
from core.system.models.os_user_logged_in import OSUserLoggedIn
from core.system.models.requests.logged_in_user_list_request import LoggedInUserListRequest


class LoggedInUsersFilter(ListDataFilter):

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    available_fields: list[str] = list(OSUserLoggedIn(user_name='').to_dict().keys())
    default_fields: list[str] = LoggedInUserListRequest().fields
