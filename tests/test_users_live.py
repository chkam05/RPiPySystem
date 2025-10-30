import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase


class UsersManagementLiveTests(SimpleTestCase):
    def config(self) -> None:
        self.base = 'https://192.168.8.142/api/auth/'
        self.username = 'root'
        self.password = 'password'
        self.auth = Authenticator(self.base, self.username, self.password)
        self.client = HttpClient(self.base, authenticator=self.auth)
    
        self.user_name = f'user_{int(time.time())}'
        self.user_id = None
    
    @testcase
    def a_create_user(self) -> None:
        body = json.dumps({'level': 'user', 'name': self.user_name, 'password': 'secret'})
        resp = self.client.post('/users/create', use_auth=True, content=body)
        self.are_equal(resp.status_code, 201)
        data = resp.json()
        self.are_equal(data.get('name'), self.user_name)
        self.are_equal(data.get('level'), 'user')
        self.is_not_null(data.get('id'))
        self.user_id = data.get('id')
    
    @testcase
    def b_list_user(self) -> None:
        resp = self.client.get('/users/list', use_auth=True, name_filter=self.user_name)
        self.are_equal(resp.status_code, 200)
        arr = resp.json()
        self.is_instance_of_type(arr, list)
        self.is_not_empty(arr)
        self.are_equal(arr[0].get('name'), self.user_name)
    
    @testcase
    def c_get_by_id(self) -> None:
        self.is_not_null(self.user_id)
        resp = self.client.get(f'/users/{self.user_id}', use_auth=True)
        self.are_equal(resp.status_code, 200)
        data = resp.json()
        self.are_equal(data.get('id'), self.user_id)
        self.are_equal(data.get('name'), self.user_name)
    
    @testcase
    def d_patch_user(self) -> None:
        new_name = f'user_{int(time.time())}'
        new_level = 'admin'

        self.is_not_null(self.user_id)
        body = json.dumps({'level': new_level, 'name': new_name, 'password': 'newsecret'})
        resp = self.client.patch(f'/users/{self.user_id}', use_auth=True, content=body)
        self.are_equal(resp.status_code, 200)
        data = resp.json()
        self.are_equal(data.get('id'), self.user_id)
        self.are_equal(data.get('name'), new_name)
        self.are_equal(data.get('level'), new_level)

        # Retake user data.
        resp = self.client.get(f'/users/{self.user_id}', use_auth=True)
        self.are_equal(resp.status_code, 200)
        data = resp.json()
        self.are_equal(data.get('id'), self.user_id)
        self.are_equal(data.get('name'), new_name)
        self.are_equal(data.get('level'), new_level)
    
    @testcase
    def e_delete_user(self) -> None:
        self.is_not_null(self.user_id)
        resp = self.client.delete(f'/users/{self.user_id}', use_auth=True)
        self.are_equal(resp.status_code, 200)
        self.is_true(resp.json().get('removed'))


if __name__ == '__main__':
    UsersManagementLiveTests().run()