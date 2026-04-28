from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote
import requests
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test.core import Authenticator, HttpClient, TestCase, testcase


AUTH_BASE_ADDRESS = 'http://127.0.0.1:5001/auth'
SUPERVISOR_BASE_ADDRESS = 'http://127.0.0.1:5002/api/supervisor'
AUTH_USERNAME = 'chkam'
AUTH_PASSWORD = 'Karpik44'

RESTART_TARGET_SERVICE = 'RaspberryPiSystem:auth_service'
STOP_START_TARGET_SERVICE = 'SERVICE_NAME'
ACTION_DELAY_SECONDS = 15

FIELD_ACTION = 'action'
FIELD_DESCRIPTION = 'description'
FIELD_FULL_NAME = 'full_name'
FIELD_GROUP = 'group'
FIELD_MESSAGE = 'message'
FIELD_NAME = 'name'
FIELD_NOW = 'now'
FIELD_PID = 'pid'
FIELD_START = 'start'
FIELD_STATE = 'state'
FIELD_STATE_CODE = 'state_code'
FIELD_STOP = 'stop'

ACTION_RESTART = 'restart'
ACTION_START = 'start'
ACTION_STOP = 'stop'

STATE_RUNNING = 'RUNNING'
STOP_ALL_ACCEPTED_STATUS_CODES = (204, 502)


class SupervisorTest(TestCase):
    def config(self) -> None:
        timeout = 60
        verify_ssl = False

        authenticator = Authenticator(
            AUTH_BASE_ADDRESS,
            AUTH_USERNAME,
            AUTH_PASSWORD,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self.client = HttpClient(
            SUPERVISOR_BASE_ADDRESS,
            authenticator=authenticator,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        self.selected_service = ''

    def _json(self, response: Any) -> Any:
        try:
            return response.json()
        except ValueError as ex:
            self.fail(f'Response is not valid JSON. Status={response.status_code}, Body={response.text!r}. Error={ex}')
        return {}

    def _assert_service_summary(self, data: Dict[str, Any]) -> None:
        self.is_not_empty(data.get(FIELD_FULL_NAME), 'Missing full_name.')
        self.is_not_empty(data.get(FIELD_NAME), 'Missing name.')
        self.is_not_empty(data.get(FIELD_GROUP), 'Missing group.')

    def _assert_service_info(self, data: Dict[str, Any]) -> None:
        self._assert_service_summary(data)
        self.is_not_empty(data.get(FIELD_STATE), 'Missing state.')
        self.is_not_null(data.get(FIELD_STATE_CODE), 'Missing state_code.')
        self.is_not_null(data.get(FIELD_DESCRIPTION), 'Missing description.')
        self.is_not_null(data.get(FIELD_NOW), 'Missing now.')
        if data.get(FIELD_START) is not None:
            self.contains(data[FIELD_START], 'T')
            self.contains(data[FIELD_START], '+00:00')
        if data.get(FIELD_STOP) is not None:
            self.contains(data[FIELD_STOP], 'T')
            self.contains(data[FIELD_STOP], '+00:00')
        self.contains(data[FIELD_NOW], 'T')
        self.contains(data[FIELD_NOW], '+00:00')

    def _assert_action_result(self, data: Dict[str, Any], expected_action: str) -> None:
        self.is_not_empty(data.get(FIELD_NAME), 'Missing action result name.')
        self.are_equal(data.get(FIELD_ACTION), expected_action)
        self.is_true(data.get(FIELD_STATE), data.get(FIELD_MESSAGE) or f'Action {expected_action} failed.')

    def _service_path(self, service_name: str) -> str:
        return quote(service_name, safe='')

    def _wait_for_state(self, service_name: str, expected_state: str, timeout_seconds: int = 60) -> Dict[str, Any]:
        deadline = time.time() + timeout_seconds
        last_data: Dict[str, Any] = {}
        service_path = self._service_path(service_name)

        while time.time() < deadline:
            response = self.client.get(f'/{service_path}')
            if response.status_code == 200:
                last_data = self._json(response)
                if last_data.get(FIELD_STATE) == expected_state:
                    return last_data
            time.sleep(1)

        self.fail(f'Service {service_name} did not reach state {expected_state}. Last data={last_data!r}')
        return last_data

    @testcase
    def test_01_list(self) -> None:
        response = self.client.get('/list')
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self.is_instance_of_type(data, list)
        self.is_not_empty(data, 'Supervisor services list should not be empty.')

        for item in data:
            self.is_instance_of_type(item, dict)
            self._assert_service_summary(item)

        self.selected_service = data[0][FIELD_FULL_NAME]

    @testcase
    def test_02_get_info(self) -> None:
        self.is_not_empty(self.selected_service, 'Missing selected service. List test should run first.')

        response = self.client.get(f'/{self._service_path(self.selected_service)}')
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_service_info(data)
        self.are_equal(data.get(FIELD_FULL_NAME), self.selected_service)

    @testcase
    def test_03_restart(self) -> None:
        response = self.client.post(f'/restart/{self._service_path(RESTART_TARGET_SERVICE)}')
        self.are_equal(response.status_code, 200, response.text)

        data = self._json(response)
        self._assert_action_result(data, ACTION_RESTART)
        time.sleep(ACTION_DELAY_SECONDS)
        self._wait_for_state(RESTART_TARGET_SERVICE, STATE_RUNNING)

    # @testcase
    # def test_04_stop_start(self) -> None:
    #     stop_response = self.client.post(f'/stop/{self._service_path(STOP_START_TARGET_SERVICE)}')
    #     self.are_equal(stop_response.status_code, 200, stop_response.text)
    #     self._assert_action_result(self._json(stop_response), ACTION_STOP)
    #     time.sleep(ACTION_DELAY_SECONDS)
    #
    #     start_response = self.client.post(f'/start/{self._service_path(STOP_START_TARGET_SERVICE)}')
    #     self.are_equal(start_response.status_code, 200, start_response.text)
    #     self._assert_action_result(self._json(start_response), ACTION_START)
    #     time.sleep(ACTION_DELAY_SECONDS)
    #     self._wait_for_state(STOP_START_TARGET_SERVICE, STATE_RUNNING)

    @testcase
    def test_05_stop_all(self) -> None:
        try:
            response = self.client.post('/stop_all')
        except requests.RequestException as ex:
            text = str(ex)
            self.assert_true(
                'RemoteDisconnected' in text or 'Connection aborted' in text,
                f'Unexpected stop_all connection error: {text}',
            )
            return

        self.assert_true(
            response.status_code in STOP_ALL_ACCEPTED_STATUS_CODES,
            f'Expected one of {STOP_ALL_ACCEPTED_STATUS_CODES}, got {response.status_code}: {response.text}',
        )
        if response.status_code == 204:
            self.is_empty(response.text)


if __name__ == '__main__':
    ok = SupervisorTest().run()
    raise SystemExit(0 if ok else 1)
