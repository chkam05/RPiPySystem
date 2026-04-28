from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test.core import HttpClient, TestCase, testcase


FIELD_ACCESS_TOKEN = 'access_token'
FIELD_EXPIRES_IN = 'expires_in'
FIELD_ID = 'id'
FIELD_IAT = 'iat'
FIELD_EXP = 'exp'
FIELD_JTI = 'jti'
FIELD_LEVEL = 'level'
FIELD_LVL = 'lvl'
FIELD_NAM = 'nam'
FIELD_NAME = 'name'
FIELD_REFRESH_TOKEN = 'refresh_token'
FIELD_REVOKED = 'revoked'
FIELD_SUB = 'sub'
FIELD_TOKEN_TYPE = 'token_type'
FIELD_TYP = 'typ'
FIELD_USER = 'user'
FIELD_VALID = 'valid'

TOKEN_TYPE_ACCESS = 'access'
TOKEN_TYPE_BEARER = 'Bearer'


class AuthTest(TestCase):
    def config(self) -> None:
        base_address = 'http://127.0.0.1:5001/auth'
        username = 'chkam'
        password = 'Karpik44'
        timeout = 30
        verify_ssl = False

        self.client = HttpClient(base_address, timeout=timeout, verify_ssl=verify_ssl)
        self.username = username
        self.password = password
        self.access_token = ''
        self.refresh_token = ''

    def _json(self, response: Any) -> Dict[str, Any]:
        try:
            return response.json()
        except ValueError as ex:
            self.fail(f'Response is not valid JSON. Status={response.status_code}, Body={response.text!r}. Error={ex}')
        return {}

    def _assert_public_user(self, data: Dict[str, Any]) -> None:
        self.is_not_empty(data.get(FIELD_ID), 'Missing user id.')
        self.are_equal(data.get(FIELD_NAME), self.username)
        self.is_not_empty(data.get(FIELD_LEVEL), 'Missing user level.')

    def _assert_token_pair(self, data: Dict[str, Any]) -> None:
        self.is_not_empty(data.get(FIELD_ACCESS_TOKEN), 'Missing access_token.')
        self.is_not_empty(data.get(FIELD_REFRESH_TOKEN), 'Missing refresh_token.')
        self.are_equal(data.get(FIELD_TOKEN_TYPE), TOKEN_TYPE_BEARER)
        self.is_positive(data.get(FIELD_EXPIRES_IN), 'expires_in should be positive.')
        self.is_instance_of_type(data.get(FIELD_USER), dict)
        self._assert_public_user(data[FIELD_USER])

    def _assert_valid_response(self, data: Dict[str, Any]) -> None:
        self.is_true(data.get(FIELD_VALID), 'Token should be valid.')
        self.is_instance_of_type(data.get(FIELD_USER), dict)
        self.is_instance_of_type(data.get(FIELD_ACCESS_TOKEN), dict)
        self._assert_public_user(data[FIELD_USER])

        access_token = data[FIELD_ACCESS_TOKEN]
        self.are_equal(access_token.get(FIELD_TYP), TOKEN_TYPE_ACCESS)
        self.is_not_empty(access_token.get(FIELD_JTI), 'Missing access token jti.')
        self.is_not_empty(access_token.get(FIELD_SUB), 'Missing access token subject.')
        self.are_equal(access_token.get(FIELD_NAM), self.username)
        self.is_not_empty(access_token.get(FIELD_LVL), 'Missing access token level.')
        self.is_positive(access_token.get(FIELD_IAT), 'Access token iat should be positive.')
        self.is_positive(access_token.get(FIELD_EXP), 'Access token exp should be positive.')

    def _auth_headers(self) -> Dict[str, str]:
        self.is_not_empty(self.access_token, 'Missing access token. Login test should run first.')
        return {'Authorization': f'Bearer {self.access_token}'}

    @testcase
    def test_01_login(self) -> None:
        request_data = {'username': self.username, 'password': self.password}
        response = self.client.post('/login', json=request_data)
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_token_pair(data)
        self.access_token = data[FIELD_ACCESS_TOKEN]
        self.refresh_token = data[FIELD_REFRESH_TOKEN]

        validate = self.client.post('/validate', headers=self._auth_headers())
        self.are_equal(validate.status_code, 200, validate.text)
        self._assert_valid_response(self._json(validate))

    @testcase
    def test_02_me(self) -> None:
        response = self.client.get('/me', headers=self._auth_headers())
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_public_user(data)

    @testcase
    def test_03_refresh(self) -> None:
        self.is_not_empty(self.refresh_token, 'Missing refresh token. Login test should run first.')

        request_data = {FIELD_REFRESH_TOKEN: self.refresh_token}
        response = self.client.post('/refresh', json=request_data)
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_token_pair(data)
        self.access_token = data[FIELD_ACCESS_TOKEN]
        self.refresh_token = data[FIELD_REFRESH_TOKEN]

        validate = self.client.post('/validate', headers=self._auth_headers())
        self.are_equal(validate.status_code, 200, validate.text)
        self._assert_valid_response(self._json(validate))

    @testcase
    def test_04_logout(self) -> None:
        self.is_not_empty(self.access_token, 'Missing access token. Login test should run first.')
        self.is_not_empty(self.refresh_token, 'Missing refresh token. Refresh test should run first.')

        request_data = {FIELD_REFRESH_TOKEN: self.refresh_token}
        response = self.client.post(
            '/logout',
            json=request_data,
            headers=self._auth_headers(),
        )
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self.is_true(data.get(FIELD_REVOKED), 'Logout should revoke tokens.')

        validate = self.client.post('/validate', headers=self._auth_headers())
        self.are_equal(validate.status_code, 401, validate.text)


if __name__ == '__main__':
    ok = AuthTest().run()
    raise SystemExit(0 if ok else 1)
