import sys
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.supervisor.service_details import ServiceDetails
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class SupervisorLiveTests(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)

        self.service: Optional[ServiceDetails] = None
    
    @testcase
    def test_01_list(self) -> None:
        # Make request
        resp = self.client.get('/supervisor/list', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_instance_of_type(data, list)
        self.is_not_empty(data)

        # Check every occurrence
        for idx, service in enumerate(data):
            self.is_instance_of_type(service, dict, f'Item #{idx} is not a dict.')
            service_details = ServiceDetails.from_dict(service)
            self.is_instance_of_type(service_details, ServiceDetails, f'Item #{idx} is not an instance of ServiceDetails.')

            if not self.service:
                self.service = service_details
            
            self.is_not_empty(service_details.full_name, f'"{ServiceDetails.FIELD_FULL_NAME}" empty in item #{idx}.')
            self.is_not_empty(service_details.name, f'"{ServiceDetails.FIELD_NAME}" empty in item #{idx}.')
            self.is_greater_than(service_details.pid, 0, f'Invalid "{ServiceDetails.FIELD_PID}" value in item #{idx}.')
            self.is_not_empty(service_details.state, f'"{ServiceDetails.FIELD_STATE}" empty in item #{idx}.')
            self.are_equal(service_details.state, 'RUNNING', f'process not RUNNING (#{idx}: {service}).')
    
    @testcase
    def test_02_details(self) -> None:
        self.is_instance_of_type(self.service, ServiceDetails)
        full_name = self.service.full_name
        pid = self.service.pid

        self.is_true(':' in full_name, 'Expected "group:name" format in full name.')
        service_group, service_name = full_name.split(':', 1)

        # Make request
        resp = self.client.get(f'/supervisor/{full_name}', use_auth=True)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        details = resp.json()
        self.is_instance_of_type(details, dict)
        service_details = ServiceDetails.from_dict(details)
        self.is_instance_of_type(service_details, ServiceDetails, f'Response is not an instance of ServiceDetails.')

        self.are_equal(service_details.full_name, full_name, f'"{ServiceDetails.FIELD_FULL_NAME}" mismatch with list full name.')
        self.are_equal(service_details.group, service_group, f'"{ServiceDetails.FIELD_GROUP}" mismatch with list full name.')
        self.are_equal(service_details.name, service_name, f'"{ServiceDetails.FIELD_NAME}" mismatch with list full name.')
        self.are_equal(service_details.pid, pid, f'"{ServiceDetails.FIELD_PID}" mismatch with list.')
        self.are_equal(service_details.state, 'RUNNING')

        if service_details.state_code is not None:
            self.are_equal(service_details.state_code, 20, f'"{ServiceDetails.FIELD_STATE_CODE}" does not indicate 20.')
        
        if service_details.description:
            self.contains(service_details.description, str(service_details.pid))
        
        if service_details.start is not None and service_details.now is not None:
            self.is_less_than(service_details.start, service_details.now, f'"{ServiceDetails.FIELD_START}" should be < "{ServiceDetails.FIELD_NOW}".')
        
        if service_details.state == 'RUNNING' and service_details.stop is not None:
            self.are_equal(service_details.stop, 0, f'"{ServiceDetails.FIELD_STOP}" should be 0 when RUNNING.')


if __name__ == '__main__':
    SupervisorLiveTests().run()