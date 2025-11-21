import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auth_service.models.access_level import AccessLevel
from auth_service.models.user import User
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH


class TestAuthSessions(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_AUTH, authenticator=self.auth)
    
    @testcase
    def test_01_sessions_me(self) -> None:
        resp = self.client.get('/sessions/me', use_auth=True)
        self.are_equal(resp.status_code, 200)
        
        data = resp.json()
        self.is_not_null(data.get(User.FIELD_ID))
        self.are_equal(data.get(User.FIELD_LEVEL), str(AccessLevel.ROOT))
        self.are_equal(data.get(User.FIELD_NAME), 'root')


if __name__ == '__main__':
    TestAuthSessions().run()