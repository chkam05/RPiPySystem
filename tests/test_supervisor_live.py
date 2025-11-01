import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from supervisor_service.models.process_details import ProcessDetails
from supervisor_service.models.process_info import ProcessInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import BASE_AUTH, BASE_SUPERVISOR


class SupervisorLiveTests(SimpleTestCase):
    def config(self) -> None:
        self.username = 'root'
        self.password = 'password'
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SUPERVISOR, authenticator=self.auth)

        self.service = None
    
    @testcase
    def test_01_supervisor_processes_list(self) -> None:
        resp = self.client.get('/processes/list', use_auth=True)
        self.are_equal(resp.status_code, 200)
        
        data = resp.json()
        self.is_instance_of_type(data, list)
        self.is_not_empty(data)

        for idx, proc in enumerate(data):
            self.is_instance_of_type(proc, dict, f'Item #{idx} is not a dict.')

            name = proc.get(ProcessInfo.FIELD_NAME)
            pid = proc.get(ProcessInfo.FIELD_PID)
            state = proc.get(ProcessInfo.FIELD_STATE)

            if not self.service:
                self.service = proc

            self.is_instance_of_type(name, str, f'"{ProcessInfo.FIELD_NAME}" type invalid in item #{idx}')
            self.is_not_empty(name, f'"{ProcessInfo.FIELD_NAME}" empty in item #{idx}')
            
            self.is_instance_of_type(pid, int, f'"{ProcessInfo.FIELD_PID}" type invalid in item #{idx}')
            self.is_greater_than(pid, 0, f'Invalid "{ProcessInfo.FIELD_PID}" value in item #{idx}')

            self.is_instance_of_type(state, str, f'"{ProcessInfo.FIELD_STATE}" type invalid in item #{idx}')
            self.is_not_empty(state, f'"{ProcessInfo.FIELD_STATE}" empty in item #{idx}')

            self.are_equal(state, 'RUNNING', f'process not RUNNING (#{idx}: {proc})')
    
    @testcase
    def test_02_supervisor_processes_list(self) -> None:
        self.is_instance_of_type(self.service, dict)
        full_name = self.service.get(ProcessInfo.FIELD_NAME)
        pid = self.service.get(ProcessInfo.FIELD_PID)

        resp = self.client.get(f'/processes/{full_name}', use_auth=True)
        self.are_equal(resp.status_code, 200)
        
        detail = resp.json()
        self.is_instance_of_type(detail, dict)
        self.is_true(':' in full_name, 'Expected "group:name" format in full name')
        service_group, service_name = full_name.split(':', 1)

        self.are_equal(detail.get(ProcessDetails.FIELD_GROUP), service_group, f'"{ProcessDetails.FIELD_GROUP}" mismatch with list full name')
        self.are_equal(detail.get(ProcessDetails.FIELD_NAME), service_name, f'"{ProcessDetails.FIELD_NAME}" mismatch with list full name')

        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_PID), int)
        self.are_equal(detail.get(ProcessDetails.FIELD_PID), pid, f'"{ProcessDetails.FIELD_PID}" mismatch with list')

        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_STATE), str)
        self.are_equal(detail.get(ProcessDetails.FIELD_STATE), 'RUNNING')

        if ProcessDetails.FIELD_STATE_CODE in detail:
            self.is_instance_of_type(detail.get(ProcessDetails.FIELD_STATE_CODE), int)
            self.are_equal(detail.get(ProcessDetails.FIELD_STATE_CODE), 20)
        
        if ProcessDetails.FIELD_DESCRIPTION in detail and isinstance(detail.get(ProcessDetails.FIELD_DESCRIPTION), str):
            self.contains(detail.get(ProcessDetails.FIELD_DESCRIPTION), str(detail.get(ProcessDetails.FIELD_PID)))
        
        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_SPAWNERR), str)
        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_STDERR_LOGFILE), str)
        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_STDOUT_LOGFILE), str)

        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_START), int)
        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_NOW), int)
        self.is_instance_of_type(detail.get(ProcessDetails.FIELD_STOP), int)

        if ProcessDetails.FIELD_START in detail and ProcessDetails.FIELD_NOW in detail:
            self.is_less_than(detail[ProcessDetails.FIELD_START], detail[ProcessDetails.FIELD_NOW], f'"{ProcessDetails.FIELD_START}" should be < "{ProcessDetails.FIELD_NOW}"')
        
        if detail.get(ProcessDetails.FIELD_STATE) == 'RUNNING' and ProcessDetails.FIELD_STOP in detail:
            self.are_equal(detail.get(ProcessDetails.FIELD_STOP), 0, f'"{ProcessDetails.FIELD_STOP}" should be 0 when RUNNING')


if __name__ == '__main__':
    SupervisorLiveTests().run()