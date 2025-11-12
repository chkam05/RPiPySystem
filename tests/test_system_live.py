from datetime import datetime
import json
import time
import sys
from pathlib import Path
from typing import List, Optional

from system_service.models.system.process_info import ProcessInfo
from system_service.models.system.process_info_request import ProcessInfoRequest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.cpu_info import CPUInfo
from system_service.models.system.os_info import OSInfo
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class SystemLiveTests(SimpleTestCase):
    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)

        self.cpu_arch: Optional[str] = None
    
    @testcase
    def test_01_info(self) -> None:
        resp = self.client.get('/info/', use_auth=True)
        self.are_equal(resp.status_code, 200)

        data = resp.json()
        self.is_instance_of_type(data, dict)
        self.is_not_empty(data)

        os_info = OSInfo.from_dict(data)
        self.is_not_null(os_info)
        self.is_instance_of_type(os_info, OSInfo)

        self.is_instance_of_type(os_info.architecture, str)
        self.is_not_empty(os_info.architecture)

        self.cpu_arch = os_info.architecture

        self.is_instance_of_type(os_info.compilation_date, datetime)
        self.is_not_null(os_info.compilation_date)
        self.is_instance_of_type(os_info.distribution, str)
        self.is_not_empty(os_info.distribution)
        self.is_instance_of_type(os_info.distribution_codename, str)
        self.is_not_empty(os_info.distribution_codename)
        self.is_instance_of_type(os_info.distribution_version, str)
        self.is_not_empty(os_info.distribution_version)
        self.is_instance_of_type(os_info.kernel, str)
        self.is_not_empty(os_info.kernel)
        self.is_instance_of_type(os_info.kernel_name, str)
        self.is_not_empty(os_info.kernel_name)
        self.is_instance_of_type(os_info.kernel_version, str)
        self.is_not_empty(os_info.kernel_version)
        self.is_instance_of_type(os_info.network_name, str)
        self.is_not_empty(os_info.network_name)
        self.is_instance_of_type(os_info.release_version, str)
        self.is_not_empty(os_info.release_version)
    
    @testcase
    def test_02_info_cpu(self) -> None:
        resp = self.client.get('/info/cpu', use_auth=True)
        self.are_equal(resp.status_code, 200)

        data = resp.json()
        self.is_instance_of_type(data, dict)
        self.is_not_empty(data)

        cpu_info = CPUInfo.from_dict(data)
        self.is_not_null(cpu_info)
        self.is_instance_of_type(cpu_info, CPUInfo)

        self.is_instance_of_type(cpu_info.architecture, str)
        self.is_not_empty(cpu_info.architecture)
        self.are_equal(cpu_info.architecture, self.cpu_arch)
        self.is_instance_of_type(cpu_info.cores_logical, int)
        self.is_greater_than_or_equal_to(cpu_info.cores_logical, 0)
        # self.is_instance_of_type(cpu_info.cores_physical, int)
        # self.is_greater_than_or_equal_to(cpu_info.cores_physical, 0)

        self.is_instance_of_type(cpu_info.freq, float)
        self.is_instance_of_type(cpu_info.freq_max, float)
        self.is_instance_of_type(cpu_info.freq_min, float)

        self.is_greater_than(cpu_info.freq_max, cpu_info.freq_min)
        self.is_less_than(cpu_info.freq_min, cpu_info.freq_max)
        self.is_in_range(cpu_info.freq, cpu_info.freq_min, cpu_info.freq_max)

        self.is_instance_of_type(cpu_info.model, str)
        self.is_not_empty(cpu_info.model)

    @testcase
    def test_03_processes(self) -> None:
        request = ProcessInfoRequest(
            process_id=True,
            parent_process_id=True,
            process_group_id=True,
            user_name=True,
            user_id=True,
            real_user_name=True,
            real_user_id=True,
            process_name=True,
            command_line=True,
            cpu_usage_percent=True,
            memory_usage_percent=True,
            cpu_process_time=True,
            elapsed_since_start=True,
            started_at=True,
            status=True,
            terminal=True,
            priority=True,
            nice_value=True,
            scheduler_class=True,
            scheduler_policy=True,
            realtime_priority=True,
            virtual_memory_kb=True,
            resident_memory_kb=True,
            current_cpu=True,
            cgroup_path=True,
            threads=True,
            wait_channel=True,
            kernel_flags=True,
            major_page_faults=True,
            minor_page_faults=True,
            session_id=True,
            thread_group_id=True
        )

        resp = self.client.post(
            '/info/processes',
            use_auth=True,
            content=json.dumps(request.to_dict())
        )
        self.are_equal(resp.status_code, 200)

        data = resp.json()
        self.is_instance_of_type(data, list)
        self.is_not_empty(data)

        processes = ProcessInfo.list_from_dicts(data)
        self.is_not_null(processes)
        self.is_instance_of_type(processes, List[ProcessInfo])


if __name__ == '__main__':
    SystemLiveTests().run()