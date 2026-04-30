from __future__ import annotations
from typing import List

from core.data_filter.list_data_filter import ListDataFilter
from core.system.models.os_user_info import OSUserInfo
from core.system.models.requests.user_list_request import UserListRequest


class UsersFilter(ListDataFilter):

    # --------------------------------------------------------------------------------
    # FIELDS
    # --------------------------------------------------------------------------------

    available_fields: list[str] = [
        OSUserInfo.FIELD_USER_NAME,
        OSUserInfo.FIELD_USER_ID,
        OSUserInfo.FIELD_GROUP_ID,
        OSUserInfo.FIELD_USER_INFO,
        OSUserInfo.FIELD_HOME_DIRECTORY,
        OSUserInfo.FIELD_SHELL_PATH,
        OSUserInfo.FIELD_CAN_LOGIN,
    ]
    default_fields: list[str] = UserListRequest().fields
