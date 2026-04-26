from datetime import datetime
import pwd
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.users.os_user_info import OSUserInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemInfoUsers(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_users(self) -> List[OSUserInfo]:
        # Make request
        resp = self.client.get('/info/users?loggable=true', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_instance_of_type(data, list)
        self.is_not_empty(data)
        self.is_instance_of_type(data[0], dict)
        self.is_not_empty(data[0])

        # Model mapping
        users = OSUserInfo.from_list_dicts(data)
        self.is_instance_of_type(users, list, f'Response is not an instance of OSUserInfo list.')

        return users

    @testcase
    def test_01_users_basic_shape(self) -> None:
        users = self._get_users()

        user = users[0]
        self.is_instance_of_type(user, OSUserInfo, f'Item in list is not an instance of OSUserInfo.')

        # Minimum sanity checks:

        # user_name
        self.is_instance_of_type(user.user_name, str)
        self.is_not_empty(user.user_name)

        # user_id
        self.is_instance_of_type(user.user_id, int)
        self.is_true(user.user_id >= 0)

        # group_id
        if user.group_id is not None:
            self.is_instance_of_type(user.group_id, int)
            self.is_true(user.group_id >= 0)
        
        # home_directory
        if user.home_directory is not None:
            self.is_instance_of_type(user.home_directory, str)

        # shell
        if user.shell_path is not None:
            self.is_instance_of_type(user.shell_path, str)

        # can_login
        self.is_instance_of_type(user.can_login, bool)
    
    @testcase
    def test_02_users_match_system(self) -> None:
        users = self._get_users()

        # Get real users from the system.
        system_users = pwd.getpwall()

        # Map of system users by name and uid:
        sys_by_name = {u.pw_name: u for u in system_users}
        sys_by_uid = {u.pw_uid: u for u in system_users}

        checked = 0

        for user in users:
            # Checking if user_name exists in the system.
            if user.user_name not in sys_by_name:
                # The user could appear in the API as artificial/system
                # but if `user_id` exists in the API, then try to match by uid.
                if user.user_id in sys_by_uid:
                    sys_entry = sys_by_uid[user.user_id]
                else:
                    # There is no reference point -> skip.
                    continue
            else:
                sys_entry = sys_by_name[user.user_name]

            # --- API - system comparisons ---

            # user_name
            self.are_equal(
                user.user_name,
                sys_entry.pw_name,
                f'{OSUserInfo.FIELD_USER_NAME} mismatch: API={user.user_name!r}, system={sys_entry.pw_name!r}.'
            )

            # user_id
            self.are_equal(
                user.user_id,
                sys_entry.pw_uid,
                f'{OSUserInfo.FIELD_USER_ID} mismatch for user {user.user_name}.'
            )

            # group_id
            if user.group_id is not None:
                self.are_equal(
                    user.group_id,
                    sys_entry.pw_gid,
                    f'{OSUserInfo.FIELD_GROUP_ID} mismatch for user {user.user_name}.'
                )

            # home_directory
            if user.home_directory is not None:
                self.are_equal(
                    user.home_directory,
                    sys_entry.pw_dir,
                    f'{OSUserInfo.FIELD_HOME_DIRECTORY} mismatch for user {user.user_name}.'
                )

            # user_info (gecos)
            if user.user_info is not None:
                self.are_equal(
                    user.user_info,
                    sys_entry.pw_gecos,
                    f'{OSUserInfo.FIELD_USER_INFO} mismatch for user {user.user_name}.'
                )

            # shell
            if user.shell_path is not None:
                self.are_equal(
                    user.shell_path,
                    sys_entry.pw_shell,
                    f'{OSUserInfo.FIELD_SHELL_PATH} mismatch for user {user.user_name}.'
                )

            checked += 1

            # Don't check all system users.
            if checked >= 15:
                break

        self.is_true(checked > 0, 'No users could be verified against system accounts.')
    
    @testcase
    def test_03_can_login_logic(self) -> None:
        users = self._get_users()

        for user in users:
            # can_login should depend on shell_path:
            # shell usually must be a real shell, NOT /usr/sbin/nologin or /bin/false.
            if user.shell_path is not None:
                shell = user.shell_path
                login_disabled_shells = {'/usr/sbin/nologin', '/bin/false'}

                if shell in login_disabled_shells:
                    self.is_false(user.can_login, f'user {user.user_name} cannot login but API returned True')
                else:
                    # normalna powłoka (bash, sh, zsh, rbash, fish...)
                    self.is_true(
                        user.can_login or user.user_id == 0,
                        f'user {user.user_name} should be able to login (shell={shell})'
                    )


if __name__ == '__main__':
    TestSystemInfoUsers().run()