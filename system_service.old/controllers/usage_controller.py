from typing import ClassVar

from flask import jsonify, request

from system_service.models.system.cpu_usage import CPUUsage
from system_service.models.system.disk_usage import DiskUsage
from system_service.models.system.mem_usage import MemUsage
from system_service.models.system.os_temp_info import OSTempInfo
from system_service.models.system.os_usage import OSUsage
from system_service.utils.os_usage_resolver import OSUsageResolver
from utils.auto_swag import auto_swag, get_bool_query_arg, ok, qparam, unauthorized
from utils.mid_auth_controller import MidAuthController


class UsageController(MidAuthController):
    _CONTROLLER_NAME: ClassVar[str] = 'system_usage'
    _CONTROLLER_PATH: ClassVar[str] = 'usage'
    _CPU_USAGE_F_SAMPLE_EXACT: ClassVar[str] = 'cpu_sample_exact'
    _CPU_USAGE_F_SAMPLE_TIME: ClassVar[str] = 'cpu_sample_time'

    def __init__(self, url_prefix_base: str, auth_url: str) -> None:
        # Fields validation:
        if not isinstance(url_prefix_base, str) or not url_prefix_base.strip():
            raise ValueError('url_prefix_base is required')
        
        url_prefix = self.join_prefix(url_prefix_base, self._CONTROLLER_PATH)

        super().__init__(self._CONTROLLER_NAME, __name__, url_prefix, auth_url)
    
    def register_routes(self) -> 'UsageController':
        self.add_url_rule('/', view_func=self.get_usage, methods=['GET'])
        self.add_url_rule('/cpu', view_func=self.get_cpu_usage, methods=['GET'])
        self.add_url_rule('/disks', view_func=self.get_disks_usage, methods=['GET'])
        self.add_url_rule('/memory', view_func=self.get_memory_usage, methods=['GET'])
        self.add_url_rule('/temperature', view_func=self.get_temperature, methods=['GET'])
        return self

    # --- ENDPOINTS ---

    @auto_swag(
        tags=['usage'],
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

        sample_exact = get_bool_query_arg(self._CPU_USAGE_F_SAMPLE_EXACT, False)

        usage = OSUsageResolver.get_cpu_usage(sample_time, sample_exact)
        return jsonify(usage.to_public()), 200

    @auto_swag(
        tags=['usage'],
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
        tags=['usage'],
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
        tags=['usage'],
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
        tags=['usage'],
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