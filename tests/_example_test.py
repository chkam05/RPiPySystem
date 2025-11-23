import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM
from utils.models.public_model import PublicModel


class ExampleTest(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_response(self) -> PublicModel:
        # Make request
        resp = self.client.get('', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_not_empty(data)
        self.is_instance_of_type(data, dict)

        # Model mapping
        model = PublicModel.from_dict(data)
        self.is_instance_of_type(model, PublicModel, f'Response is not an instance of PublicModel.')

        return model

    @testcase
    def test_01_model(self) -> None:
        model = self._get_response()
        self.is_true(True)


if __name__ == '__main__':
    ExampleTest().run()