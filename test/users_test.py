from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test.core import Authenticator, HttpClient, TestCase, testcase


FIELD_ID = 'id'
FIELD_LEVEL = 'level'
FIELD_NAME = 'name'
FIELD_PASSWORD = 'password'
FIELD_REMOVED = 'removed'

LEVEL_USER = 'user'


class UsersTest(TestCase):
    def config(self) -> None:
        base_address = 'http://127.0.0.1:5001/auth'
        username = 'chkam'
        password = 'Karpik44'
        timeout = 30
        verify_ssl = False

        suffix = str(int(time.time() * 1000))
        self.test_user_name = f'test_user_{suffix}'
        self.updated_user_name = f'test_user_updated_{suffix}'
        self.test_user_password = 'TestUser44'
        self.updated_user_password = 'TestUser55'
        self.test_user_id = ''

        authenticator = Authenticator(base_address, username, password, timeout=timeout, verify_ssl=verify_ssl)
        self.client = HttpClient(base_address, authenticator=authenticator, timeout=timeout, verify_ssl=verify_ssl)

    def _json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as ex:
            self.fail(f'Response is not valid JSON. Status={response.status_code}, Body={response.text!r}. Error={ex}')
        return {}

    def _assert_user(self, data: Dict[str, Any], expected_name: str, expected_level: str = LEVEL_USER) -> None:
        self.is_not_empty(data.get(FIELD_ID), 'Missing user id.')
        self.are_equal(data.get(FIELD_NAME), expected_name)
        self.are_equal(data.get(FIELD_LEVEL), expected_level)

    def _find_user(self, users: List[Dict[str, Any]], user_id: str) -> Dict[str, Any] | None:
        for user in users:
            if user.get(FIELD_ID) == user_id:
                return user
        return None

    @testcase
    def test_01_create_user(self) -> None:
        request_data = {
            FIELD_NAME: self.test_user_name,
            FIELD_PASSWORD: self.test_user_password,
            FIELD_LEVEL: LEVEL_USER,
        }
        response = self.client.post('/users/create', json=request_data)
        self.are_equal(response.status_code, 201, response.text)

        data = self._json(response)
        self._assert_user(data, self.test_user_name)
        self.test_user_id = data[FIELD_ID]

    @testcase
    def test_02_list_users(self) -> None:
        self.is_not_empty(self.test_user_id, 'Missing test user id. Create user test should run first.')

        response = self.client.get('/users/list', name_filter=self.test_user_name, level_filter=LEVEL_USER)
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self.is_instance_of_type(data, list)

        found = self._find_user(data, self.test_user_id)
        self.is_not_null(found, 'Created user was not found on users list.')
        self._assert_user(found, self.test_user_name)

    @testcase
    def test_03_get_user(self) -> None:
        self.is_not_empty(self.test_user_id, 'Missing test user id. Create user test should run first.')

        response = self.client.get(f'/users/{self.test_user_id}')
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_user(data, self.test_user_name)

    @testcase
    def test_04_update_user(self) -> None:
        self.is_not_empty(self.test_user_id, 'Missing test user id. Create user test should run first.')

        request_data = {
            FIELD_NAME: self.updated_user_name,
            FIELD_PASSWORD: self.updated_user_password,
            FIELD_LEVEL: LEVEL_USER,
        }
        response = self.client.patch(f'/users/{self.test_user_id}', json=request_data)
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_user(data, self.updated_user_name)

        get_response = self.client.get(f'/users/{self.test_user_id}')
        self.are_equal(get_response.status_code, 200, get_response.text)
        self._assert_user(self._json(get_response), self.updated_user_name)

    @testcase
    def test_05_remove_user(self) -> None:
        self.is_not_empty(self.test_user_id, 'Missing test user id. Create user test should run first.')

        response = self.client.delete(f'/users/{self.test_user_id}')
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self.is_true(data.get(FIELD_REMOVED), 'User should be removed.')

        get_response = self.client.get(f'/users/{self.test_user_id}')
        self.are_equal(get_response.status_code, 404, get_response.text)


if __name__ == '__main__':
    ok = UsersTest().run()
    raise SystemExit(0 if ok else 1)
