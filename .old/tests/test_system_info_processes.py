from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from system_service.models.system.processes.process_info import ProcessInfo
from system_service.models.system.processes.process_info_request import ProcessInfoRequest
from tests.common.authenticator import Authenticator
from tests.common.http_client import HttpClient
from tests.common.test_framework import SimpleTestCase, testcase
from tests.conf import AUTH_LOGIN, AUTH_PASSWORD, BASE_AUTH, BASE_SYSTEM


class TestSystemInfoProcesses(SimpleTestCase):
    _REQUEST_BODY = ProcessInfoRequest(
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

    def config(self) -> None:
        self.username = AUTH_LOGIN
        self.password = AUTH_PASSWORD
        self.auth = Authenticator(BASE_AUTH, self.username, self.password)
        self.client = HttpClient(BASE_SYSTEM, authenticator=self.auth)
    
    def _get_processes(self) -> List[ProcessInfo]:
        # Make request
        request_content = json.dumps(self._REQUEST_BODY.to_dict())
        resp = self.client.post('/info/processes', use_auth=True, content=request_content)
        self.are_equal(resp.status_code, 200)

        # Retrieve data
        data = resp.json()
        self.is_instance_of_type(data, list)
        self.is_not_empty(data)
        self.is_instance_of_type(data[0], dict)
        self.is_not_empty(data[0])

        # Model mapping
        processes = ProcessInfo.from_list_dicts(data)
        self.is_instance_of_type(processes, list, f'Response is not an instance of ProcessInfo list.')

        return processes

    @testcase
    def test_01_processes_basic_shape(self) -> None:
        processes = self._get_processes()

        proc = processes[0]
        self.is_instance_of_type(proc, ProcessInfo, f'Item in list is not an instance of ProcessInfo.')

        # --- PID / IDs ---
        if proc.process_id is not None:
            self.is_instance_of_type(proc.process_id, int)
            self.is_true(proc.process_id > 0, 'PID should be positive')
        
        if proc.parent_process_id is not None:
            self.is_instance_of_type(proc.parent_process_id, int)
        
        if proc.process_group_id is not None:
            self.is_instance_of_type(proc.process_group_id, int)
        
        # --- names / commands ---
        if proc.process_name is not None:
            self.is_instance_of_type(proc.process_name, str)
            self.is_not_empty(proc.process_name)

        if proc.command_line is not None:
            self.is_instance_of_type(proc.command_line, str)
            # cmdline can be empty sometimes, so don't force it to be non-empty.
        
        # --- CPU / MEM % ---
        if proc.cpu_usage_percent is not None:
            self.is_instance_of_type(proc.cpu_usage_percent, float)
            self.is_true(0.0 <= proc.cpu_usage_percent <= 100.0,
                         '%CPU must be in [0, 100]')

        if proc.memory_usage_percent is not None:
            self.is_instance_of_type(proc.memory_usage_percent, float)
            self.is_true(0.0 <= proc.memory_usage_percent <= 100.0,
                         '%MEM must be in [0, 100]')
        
        # --- times ---
        if proc.cpu_process_time is not None:
            self.is_instance_of_type(proc.cpu_process_time, timedelta)
            self.is_true(proc.cpu_process_time.total_seconds() >= 0)

        if proc.elapsed_since_start is not None:
            self.is_instance_of_type(proc.elapsed_since_start, timedelta)
            self.is_true(proc.elapsed_since_start.total_seconds() >= 0)
        
        # --- memory usage ---
        if proc.virtual_memory_kb is not None:
            self.is_instance_of_type(proc.virtual_memory_kb, int)
            self.is_true(proc.virtual_memory_kb >= 0)

        if proc.resident_memory_kb is not None:
            self.is_instance_of_type(proc.resident_memory_kb, int)
            self.is_true(proc.resident_memory_kb >= 0)

        # --- threads ---
        if proc.threads is not None:
            self.is_instance_of_type(proc.threads, int)
            self.is_true(proc.threads >= 1, 'Number of threads should be >= 1')
    
    @testcase
    def test_02_processes_match_proc(self) -> None:
        processes = self._get_processes()
        checked = 0

        # Check the first N processes to avoid going through the entire list.
        MAX_CHECKED = 10
        for proc in processes:
            if proc.process_id is None:
                continue
            
            pid = proc.process_id
            proc_dir = f'/proc/{pid}'

            # The process may have disappeared between the API call and the test -> then skip:
            if not os.path.isdir(proc_dir):
                continue

            # --- /proc/<pid>/comm vs process_name ---
            if proc.process_name is not None:
                try:
                    with open(os.path.join(proc_dir, 'comm'), 'r') as f:
                        comm_name = f.read().strip()
                    self.are_equal(
                        proc.process_name,
                        comm_name,
                        f'API process_name ({proc.process_name!r}) does not match /proc/{pid}/comm ({comm_name!r}).'
                    )
                except Exception:
                    # If comm can't be read, that's fine - but don't let that break the whole test.
                    pass
            
            # --- /proc/<pid>/cmdline vs command_line ---
            if proc.command_line is not None:
                try:
                    with open(os.path.join(proc_dir, 'cmdline'), 'rb') as f:
                        raw = f.read()
                    # In /proc/<pid>/cmdline, arguments are separated by \x00.
                    system_cmdline = raw.replace(b'\x00', b' ').decode(errors='ignore').strip()

                    if system_cmdline:
                        # The API can add/cut things, so it checks
                        # that the cmdline from /proc is prefixed to or equal to that of the API.
                        api_cmdline = proc.command_line.strip()
                        self.is_true(
                            api_cmdline.startswith(system_cmdline) or
                            system_cmdline.startswith(api_cmdline),
                            f'API cmdline ({api_cmdline!r}) is not consistent with /proc/{pid}/cmdline ({system_cmdline!r}).'
                        )
                except Exception:
                    # If reading fails (very short-lived process etc.)
                    pass
            
            checked += 1
            if checked >= MAX_CHECKED:
                break
        
        # Make sure, that something has actually been checked.
        self.is_true(checked > 0, 'No processes could be verified against /proc.')

if __name__ == '__main__':
    TestSystemInfoProcesses().run()