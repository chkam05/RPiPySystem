from __future__ import annotations
from datetime import datetime
import pwd

from core.system.models.os_user_info import OSUserInfo
from core.system.models.os_user_logged_in import OSUserLoggedIn
from core.system.utilities._helpers import psutil, run_command


class UserInfoUtility:
    LOGIN_SHELLS = {'/bin/bash', '/bin/dash', '/bin/sh', '/bin/zsh', '/bin/fish'}
    DISABLED_SHELLS = {'/usr/sbin/nologin', '/sbin/nologin', '/bin/false', '/usr/bin/false'}

    def get_users(self) -> list[OSUserInfo]:
        return [
            self._user_from_pwd(user)
            for user in pwd.getpwall()
        ]

    def get_user_by_id_or_name(self, idname: str) -> OSUserInfo | None:
        try:
            if str(idname).isdigit():
                return self._user_from_pwd(pwd.getpwuid(int(idname)))

            return self._user_from_pwd(pwd.getpwnam(idname))
        except KeyError:
            return None

    def get_logged_in_users(self) -> list[OSUserLoggedIn]:
        result = self._get_psutil_users()
        if result:
            return result

        return self._get_who_users()

    def get_logged_in_users_by_name(self, name: str) -> list[OSUserLoggedIn]:
        return [user for user in self.get_logged_in_users() if user.user_name == name]

    def get_logged_in_user_by_name(self, name: str) -> OSUserLoggedIn | None:
        users = self.get_logged_in_users_by_name(name)
        return users[0] if users else None

    def _get_psutil_users(self) -> list[OSUserLoggedIn]:
        if not psutil:
            return []

        users: list[OSUserLoggedIn] = []
        for user in psutil.users():
            users.append(self._logged_in_user_from_psutil(user))

        return users

    def _get_who_users(self) -> list[OSUserLoggedIn]:
        output = run_command(['who', '-u'])
        if not output:
            return []

        users: list[OSUserLoggedIn] = []
        for line in output.splitlines():
            user = self._logged_in_user_from_who_line(line)
            if user:
                users.append(user)

        return users

    def _get_who_user_by_name(self, name: str) -> OSUserLoggedIn | None:
        output = run_command(['who', '-u'])
        if not output:
            return None

        for line in output.splitlines():
            user = self._logged_in_user_from_who_line(line)
            if user and user.user_name == name:
                return user

        return None

    def _can_login(self, uid: int, shell: str) -> bool:
        if not shell or shell in self.DISABLED_SHELLS:
            return False

        return uid >= 1000 or shell in self.LOGIN_SHELLS

    def _user_from_pwd(self, user) -> OSUserInfo:
        return OSUserInfo(
            user_name=user.pw_name,
            user_id=user.pw_uid,
            group_id=user.pw_gid,
            user_info=user.pw_gecos or None,
            home_directory=user.pw_dir or None,
            shell_path=user.pw_shell or None,
            can_login=self._can_login(user.pw_uid, user.pw_shell),
        )

    def _logged_in_user_from_psutil(self, user) -> OSUserLoggedIn:
        return OSUserLoggedIn(
            user_name=user.name,
            terminal_name=user.terminal or None,
            logged_at=datetime.fromtimestamp(user.started) if user.started else None,
            remote_host=user.host or None,
            process_id=user.pid,
        )

    def _logged_in_user_from_who_line(self, line: str) -> OSUserLoggedIn | None:
        parts = line.split()
        if len(parts) < 5:
            return None
        logged_at = self._parse_who_datetime(parts[2], parts[3])
        return OSUserLoggedIn(
            user_name=parts[0],
            terminal_name=parts[1],
            logged_at=logged_at,
            remote_host=parts[-1].strip('()') if parts[-1].startswith('(') else None,
        )

    def _parse_who_datetime(self, date_value: str, time_value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(f'{date_value}T{time_value}:00')
        except ValueError:
            return None
