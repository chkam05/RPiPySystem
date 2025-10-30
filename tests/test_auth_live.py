import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase


class AuthLiveTests(SimpleTestCase):
    def config(self) -> None:
        self.base = 'https://192.168.8.142/api/auth/'
        self.username = 'root'
        self.password = 'password'
        self.auth = Authenticator(self.base, self.username, self.password)
        self.client = HttpClient(self.base, authenticator=self.auth)
    
    @testcase
    def login_me_endpoint_returns_user(self) -> None:
        resp = self.client.get('/sessions/me', use_auth=True)
        self.are_equal(resp.status_code, 200)
        data = resp.json()
        self.is_not_null(data.get('id'))
        self.are_equal(data.get('level'), 'root')
        self.are_equal(data.get('name'), 'root')


if __name__ == '__main__':
    AuthLiveTests().run()