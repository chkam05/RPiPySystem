import json
import time
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
from tests.conf import BASE_AUTH


class UsersManagementLiveTests(SimpleTestCase):
    def config(self) -> None:
        self.username = 'root'
        self.password = 'password'
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_AUTH, authenticator=self.auth)
    
        self.user_name = f'user_{int(time.time())}'
        self.user_id = None
    
    @testcase
    def test_01_user_create(self) -> None:
        body = json.dumps({
            User.FIELD_LEVEL: str(AccessLevel.USER),
            User.FIELD_NAME: self.user_name,
            User.FIELD_PASSWORD: 'secret'
        })
        resp = self.client.post('/users/create', use_auth=True, content=body)
        self.are_equal(resp.status_code, 201)

        data = resp.json()
        self.are_equal(data.get(User.FIELD_NAME), self.user_name)
        self.are_equal(data.get(User.FIELD_LEVEL), str(AccessLevel.USER))
        self.is_not_null(data.get(User.FIELD_ID))
        self.user_id = data.get(User.FIELD_ID)
    
    @testcase
    def test_02_user_list(self) -> None:
        resp = self.client.get('/users/list', use_auth=True, name_filter=self.user_name)
        self.are_equal(resp.status_code, 200)

        arr = resp.json()
        self.is_instance_of_type(arr, list)
        self.is_not_empty(arr)
        self.are_equal(arr[0].get(User.FIELD_NAME), self.user_name)
    
    @testcase
    def test_03_user_get(self) -> None:
        self.is_not_null(self.user_id)
        resp = self.client.get(f'/users/{self.user_id}', use_auth=True)
        self.are_equal(resp.status_code, 200)

        data = resp.json()
        self.are_equal(data.get(User.FIELD_ID), self.user_id)
        self.are_equal(data.get(User.FIELD_NAME), self.user_name)
    
    @testcase
    def test_04_user_patch(self) -> None:
        new_name = f'user_{int(time.time())}'
        new_level = str(AccessLevel.ADMIN)

        self.is_not_null(self.user_id)
        body = json.dumps({
            User.FIELD_LEVEL: new_level,
            User.FIELD_NAME: new_name,
            User.FIELD_PASSWORD: 'newsecret'
        })
        resp = self.client.patch(f'/users/{self.user_id}', use_auth=True, content=body)
        self.are_equal(resp.status_code, 200)

        data = resp.json()
        self.are_equal(data.get(User.FIELD_ID), self.user_id)
        self.are_equal(data.get(User.FIELD_NAME), new_name)
        self.are_equal(data.get(User.FIELD_LEVEL), new_level)

        # Retake user data.
        resp = self.client.get(f'/users/{self.user_id}', use_auth=True)
        self.are_equal(resp.status_code, 200)
        
        data = resp.json()
        self.are_equal(data.get(User.FIELD_ID), self.user_id)
        self.are_equal(data.get(User.FIELD_NAME), new_name)
        self.are_equal(data.get(User.FIELD_LEVEL), new_level)
    
    @testcase
    def test_05_user_delete(self) -> None:
        self.is_not_null(self.user_id)
        resp = self.client.delete(f'/users/{self.user_id}', use_auth=True)
        self.are_equal(resp.status_code, 200)
        self.is_true(resp.json().get('removed'))


if __name__ == '__main__':
    UsersManagementLiveTests().run()