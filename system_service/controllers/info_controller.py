from typing import ClassVar

from flask import jsonify, request
from supervisor_service.models.process_info import ProcessInfo
from system_service.models.system.disk_usage import DiskUsage
from system_service.models.system.mem_usage import MemUsage
from system_service.models.system.os_info import OSInfo
from system_service.models.system.os_temp_info import OSTempInfo
from system_service.models.system.os_usage import OSUsage
from system_service.models.system.cpu_info import CPUInfo
from system_service.models.system.cpu_usage import CPUUsage
from system_service.models.system.process_info_request import ProcessInfoRequest
from system_service.utils.os_info_resolver import OSInfoResolver
from system_service.utils.os_usage_resolver import OSUsageResolver
from system_service.utils.process_info_resolver import ProcessInfoResolver
from utils.auto_swag import auto_swag, ok, qparam, request_body_json, unauthorized
from utils.format_util import FormatUtil
from utils.mid_auth_controller import MidAuthController


class InfoController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_info'
    _CONTROLLER_PATH: ClassVar[str] = 'info'
    _CPU_USAGE_F_SAMPLE_EXACT: ClassVar[str] = 'cpu_sample_exact'
    _CPU_USAGE_F_SAMPLE_TIME: ClassVar[str] = 'cpu_sample_time'

    def __init__(self, url_prefix_base: str, auth_url: str) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'InfoController':
        self.add_url_rule('/', view_func=self.get_info, methods=['GET'])
        self.add_url_rule('/cpu', view_func=self.get_cpu_info, methods=['GET'])
        self.add_url_rule('/processes', view_func=self.get_processes, methods=['POST'])
        self.add_url_rule('/usage', view_func=self.get_usage, methods=['GET'])
        self.add_url_rule('/usage/cpu', view_func=self.get_cpu_usage, methods=['GET'])
        self.add_url_rule('/usage/disks', view_func=self.get_disks_usage, methods=['GET'])
        self.add_url_rule('/usage/memory', view_func=self.get_memory_usage, methods=['GET'])
        self.add_url_rule('/usage/temperature', view_func=self.get_temperature, methods=['GET'])
        return self

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['system'],
        summary='Get information about the operating system — Root Only',
        description='Returns information about the operating system on which the service is running.',
        responses={
            200: ok(OSInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        info = OSInfoResolver.get_os_info()
        return jsonify(info.to_public()), 200
    
    @auto_swag(
        tags=['system'],
        summary='Get information about the processor — Root Only',
        description='Returns information about the processor.',
        responses={
            200: ok(CPUInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_cpu_info(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        cpu_info = OSUsageResolver.get_cpu_info()
        return jsonify(cpu_info.to_public()), 200

    @auto_swag(
        tags=['system'],
        summary='Get list of current processes — Root Only',
        description='Returns list of processes currently running in system.',
        request_body=request_body_json(ProcessInfoRequest.schema_get_request()),
        responses={
            200: ok(ProcessInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_processes(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        raw_data = request.get_json(silent=True)
        data = ProcessInfoRequest.from_dict(raw_data) if raw_data else ProcessInfoRequest.default()

        processes = ProcessInfoResolver.get_process_infos(data)
        processes_dict = ProcessInfo.list_to_public(processes)
        keep_null_fields = [k for k, v in data.to_dict().items() if v is True]

        return jsonify(FormatUtil.list_without_nulls(processes_dict, keep_null_fields)), 200

    @auto_swag(
        tags=['system'],
        summary='Get real-time system CPU usage statistics — Root Only',
        description='Returns current CPU usage of the system.',
        parameters=[
            qparam(_CPU_USAGE_F_SAMPLE_TIME, {'type': 'number', 'example': 3.0}, 'Sampling duration in seconds for CPU usage measurement.'),
            qparam(_CPU_USAGE_F_SAMPLE_EXACT, {'type': 'boolean', 'example': False}, 'Enables precise tick-based CPU sampling using the full cpu_sample_time interval.')
        ],
        responses={
            200: ok(CPUUsage.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_cpu_usage(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code
        
        sample_time = request.args.get(
            self._CPU_USAGE_F_SAMPLE_TIME,
            type=float,
            default=OSUsageResolver.CPU_SAMPLE_SECONDS
        )

        sample_exact = request.args.get(
            self._CPU_USAGE_F_SAMPLE_EXACT,
            type=bool,
            default=False
        )

        usage = OSUsageResolver.get_cpu_usage(sample_time, sample_exact)
        return jsonify(usage.to_public()), 200

    @auto_swag(
        tags=['system'],
        summary='Get real-time system disk usage statistics — Root Only',
        description='Returns current disk usage of the system.',
        responses={
            200: ok(DiskUsage.schema_public_list()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_disks_usage(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        disks = OSUsageResolver.get_disks()
        return jsonify(DiskUsage.list_to_public(disks)), 200

    @auto_swag(
        tags=['system'],
        summary='Get real-time system memory usage statistics — Root Only',
        description='Returns current memory usage of the system.',
        responses={
            200: ok(MemUsage.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_memory_usage(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        memory = OSUsageResolver.get_memory_usage()
        return jsonify(memory.to_public()), 200

    @auto_swag(
        tags=['system'],
        summary='Get real-time system temperature — Root Only',
        description='Returns current temperature of the system.',
        responses={
            200: ok(OSTempInfo.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_temperature(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        temperature = OSUsageResolver.get_temperature()
        return jsonify(temperature.to_public()), 200

    @auto_swag(
        tags=['system'],
        summary='Get real-time system usage statistics — Root Only',
        description='Returns current CPU, memory, disk, and temperature usage of the system.',
        responses={
            200: ok(OSUsage.schema_public()),
            401: unauthorized('Missing/invalid token'),
        },
    )
    def get_usage(self):
        ok_, err, code = self._require_root()
        if not ok_:
            return jsonify(err), code

        usage = OSUsageResolver.get_os_usage()
        return jsonify(usage.to_public()), 200