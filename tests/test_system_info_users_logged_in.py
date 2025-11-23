from datetime import datetime, timedelta
import os
import pwd
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.users.os_user_logged_in import OSUserLoggedIn
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemInfoUsersLoggedIn(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_users_logged_in(self) -> List[OSUserLoggedIn]:
        # Make request
        resp = self.client.get('/info/users/logged_in', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_instance_of_type(data, list)
        self.is_not_empty(data)

        # Model mapping
        users = OSUserLoggedIn.from_list_dicts(data)
        self.is_instance_of_type(users, list, f'Response is not an instance of OSUserLoggedIn list.')

        return users

    def _get_who_user_terminal_pairs(self) -> list[tuple[str, str]]:
        """
        Runs `who` and extracts (user, terminal) pairs.
        The format of `who` lines may vary, so parse very carefully.
        Returns an empty list if `who` is unavailable or cannot be parsed.
        """
        try:
            # `who -u` gives additional information (idle, pid), but for us the first 2 columns are important.
            proc = subprocess.run(
                ["who", "-u"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
        except Exception:
            return []

        pairs: list[tuple[str, str]] = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue

            # typical format: "user pts/0 2025-11-23 12:34 old 1234 (:0)"
            parts = line.split()
            if len(parts) < 2:
                continue

            user = parts[0]
            tty = parts[1]

            pairs.append((user, tty))

        return pairs

    @testcase
    def test_01_logged_in_basic_shape(self) -> None:
        users = self._get_users_logged_in()

        # It may happen that no one is logged in – then the list may be empty.
        # If it is not empty, check the first element more carefully.
        if not users or not any(users):
            return
        
        user = users[0]
        self.is_instance_of_type(user, OSUserLoggedIn, f'Item in list is not an instance of OSUserLoggedIn.')

        # user_name
        self.is_instance_of_type(user.user_name, str)
        self.is_not_empty(user.user_name)

        # terminal_name
        if user.terminal_name is not None:
            self.is_instance_of_type(user.terminal_name, str)
            self.is_not_empty(user.terminal_name)
        
        # logged_at
        if user.logged_at is not None:
            self.is_instance_of_type(user.logged_at, datetime)
        
        # idle_time
        if user.idle_time is not None:
            self.is_instance_of_type(user.idle_time, timedelta)
            self.is_true(user.idle_time.total_seconds() >= 0)
        
        # job_cpu_time / process_cpu_time – number of seconds, if any.
        for val in (user.job_cpu_time, user.process_cpu_time):
            if val is not None:
                self.is_instance_of_type(val, float)
                self.is_true(val >= 0.0)

        # process_id – if it is, then positive int.
        if user.process_id is not None:
            self.is_instance_of_type(user.process_id, int)
            self.is_true(user.process_id > 0)

        # session_command – if it is, then string.
        if user.session_command is not None:
            self.is_instance_of_type(user.session_command, str)
    
    @testcase
    def test_02_logged_in_users_exist_in_system(self) -> None:
        users = self._get_users_logged_in()

        if not users or not any(users):
            # No one is logged in - this is allowed.
            return

        for u in users:
            # Each user_name from the API should exist in the system.
            try:
                pwd_entry = pwd.getpwnam(u.user_name)
            except KeyError:
                self.fail(f'Logged-in user from API ({u.user_name!r}) does not exist in /etc/passwd.')
                continue

            # sanity: uid >= 0
            self.is_true(pwd_entry.pw_uid >= 0)
    
    @testcase
    def test_03_logged_in_match_proc_and_who(self) -> None:
        users = self._get_users_logged_in()

        if not users or not any(users):
            # No one is logged in - this is allowed.
            return

        # --- process_id -> /proc/PID exists ---
        checked_pids = 0
        for u in users:
            if u.process_id is None:
                continue

            proc_dir = f"/proc/{u.process_id}"
            if os.path.isdir(proc_dir):
                checked_pids += 1
            # If /proc/<pid> does not exist, the process may have already terminated
            # do not treat this as an error.

        # There is no requirement for everyone to have PID, but if there were any,
        # then at least one must have actually been in /proc.
        if any(u.process_id is not None for u in users):
            self.is_true(checked_pids > 0, 'No process IDs from API existed in /proc at test time.')

        # --- Compliance with `who` (user + terminal) – best effort ---
        who_entries = self._get_who_user_terminal_pairs()

        # If `who` doesn't work or returns nothing, don't force the assertion.
        if not who_entries:
            return

        # Building a set of (user, terminal) pairs from the API.
        api_pairs = {
            (u.user_name, u.terminal_name)
            for u in users
            if u.terminal_name is not None
        }

        # and the set of pairs with `who`.
        who_pairs = set(who_entries)

        # Checking that at least one API session exists in `who`.
        common = api_pairs & who_pairs
        self.is_true(
            len(common) > 0,
            f'No (user, terminal) pair from API matches output of `who` (API={api_pairs}, who={who_pairs}).'
        )


if __name__ == '__main__':
    TestSystemInfoUsersLoggedIn().run()