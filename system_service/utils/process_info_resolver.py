from datetime import datetime, timedelta
import subprocess
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Union

from system_service.models.system.process_info import ProcessInfo
from system_service.models.system.process_info_dto import ProcessInfoDto
from system_service.models.system.process_info_request import ProcessInfoRequest


class ProcessInfoResolver:
    """Resolve process information using ps command."""

    # Map ps column name -> fixed width (for :WIDTH spec)
    _PS_COLUMN_WIDTHS: ClassVar[Dict[str, int]] = {
        'pid': 6,
        'ppid': 6,
        'pgid': 6,
        'uid': 4,
        'ruid': 4,
        'pri': 4,
        'priority': 4,
        'vsz': 8,
        'rss': 8,
        'psr': 2,
        'nlwp': 2,
        'thcount': 1,
        'flags': 1,
        'f': 1,
        'maj_flt': 8,
        'min_flt': 8,
        'sid': 6,
        'tgid': 6,
        'sess': 6,
        '%cpu': 6,
        '%mem': 6,
        'stat': 4,
        'state': 4,
        'tty': 16,
        'nice': 4,
        'cls': 4,
        'policy': 4,
        'rtprio': 4,
        'cpu': 4,
        'user': 32,
        'ruser': 32,
        'cgroup': 128,
        'wchan': 32,
        'cputime': 16,
        'time': 16,
        'etime': 24,
        'start': 16,
        'start_time': 16,
        'lstart': 32,
        'comm': 64,
        'args': 512,
        'cmd': 512,
    }

    # Map ps column name -> DTO field name
    _PS_COLUMN_TO_DTO_FIELD: ClassVar[Dict[str, str]] = {
        'pid': ProcessInfoDto.FIELD_PID,
        'ppid': ProcessInfoDto.FIELD_PPID,
        'pgid': ProcessInfoDto.FIELD_PGID,
        'uid': ProcessInfoDto.FIELD_UID,
        'ruid': ProcessInfoDto.FIELD_RUID,
        'pri': ProcessInfoDto.FIELD_PRI,
        'priority': ProcessInfoDto.FIELD_PRIORITY,
        'vsz': ProcessInfoDto.FIELD_VSZ,
        'rss': ProcessInfoDto.FIELD_RSS,
        'psr': ProcessInfoDto.FIELD_PSR,
        'nlwp': ProcessInfoDto.FIELD_NLWP,
        'thcount': ProcessInfoDto.FIELD_THCOUNT,
        'flags': ProcessInfoDto.FIELD_FLAGS,
        'f': ProcessInfoDto.FIELD_F,
        'maj_flt': ProcessInfoDto.FIELD_MAJ_FLT,
        'min_flt': ProcessInfoDto.FIELD_MIN_FLT,
        'sid': ProcessInfoDto.FIELD_SID,
        'tgid': ProcessInfoDto.FIELD_TGID,
        'sess': ProcessInfoDto.FIELD_SESS,
        '%cpu': ProcessInfoDto.FIELD_PCPU,
        '%mem': ProcessInfoDto.FIELD_PMEM,
        'stat': ProcessInfoDto.FIELD_STAT,
        'state': ProcessInfoDto.FIELD_STATE,
        'tty': ProcessInfoDto.FIELD_TTY,
        'nice': ProcessInfoDto.FIELD_NICE,
        'cls': ProcessInfoDto.FIELD_CLS,
        'policy': ProcessInfoDto.FIELD_POLICY,
        'rtprio': ProcessInfoDto.FIELD_RTPRIO,
        'cpu': ProcessInfoDto.FIELD_CPU,
        'user': ProcessInfoDto.FIELD_USER,
        'ruser': ProcessInfoDto.FIELD_RUSER,
        'cgroup': ProcessInfoDto.FIELD_CGROUP,
        'wchan': ProcessInfoDto.FIELD_WCHAN,
        'cputime': ProcessInfoDto.FIELD_CPUTIME,
        'time': ProcessInfoDto.FIELD_TIME,
        'etime': ProcessInfoDto.FIELD_ETIME,
        'start': ProcessInfoDto.FIELD_START,
        'start_time': ProcessInfoDto.FIELD_START_TIME,
        'lstart': ProcessInfoDto.FIELD_LSTART,
        'comm': ProcessInfoDto.FIELD_COMM,
        'args': ProcessInfoDto.FIELD_ARGS,
        'cmd': ProcessInfoDto.FIELD_CMD,
    }

    # DTO fields that should be converted to int
    _INT_FIELDS: ClassVar[set] = {
        ProcessInfoDto.FIELD_PID,
        ProcessInfoDto.FIELD_PPID,
        ProcessInfoDto.FIELD_PGID,
        ProcessInfoDto.FIELD_UID,
        ProcessInfoDto.FIELD_RUID,
        ProcessInfoDto.FIELD_PRI,
        ProcessInfoDto.FIELD_VSZ,
        ProcessInfoDto.FIELD_RSS,
        ProcessInfoDto.FIELD_PSR,
        ProcessInfoDto.FIELD_NLWP,
        ProcessInfoDto.FIELD_F,
        ProcessInfoDto.FIELD_MAJ_FLT,
        ProcessInfoDto.FIELD_MIN_FLT,
        ProcessInfoDto.FIELD_SID,
        ProcessInfoDto.FIELD_TGID,
        ProcessInfoDto.FIELD_NICE,
    }

    # DTO fields that should be converted to float
    _FLOAT_FIELDS: ClassVar[set] = {
        ProcessInfoDto.FIELD_PCPU,
        ProcessInfoDto.FIELD_PMEM,
    }

    # Month names for lstart parsing (English + Polish)
    _MONTHS: ClassVar[Dict[str, int]] = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12,
        'sty': 1,
        'lut': 2,
        'mar': 3,
        'kwi': 4,
        'maj': 5,
        'cze': 6,
        'lip': 7,
        'sie': 8,
        'wrz': 9,
        'paź': 10,
        'paz': 10,
        'październik': 10,
        'lis': 11,
        'gru': 12,
    }


    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation of this static utility class.
        """
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')

    # --------------------------------------------------------------------------
    # --- BUILD AND RUN ps COMMAND METHODS. ---
    # --------------------------------------------------------------------------

    @classmethod
    def _build_ps_plan(cls, request: ProcessInfoRequest) -> List[tuple]:
        """
        Build ps column plan based on request.
        """
        plan: List[tuple] = []
        used_columns: set = set()

        def add(ps_col: str) -> None:
            if ps_col in used_columns:
                return
            if ps_col not in cls._PS_COLUMN_WIDTHS:
                return
            dto_field = cls._PS_COLUMN_TO_DTO_FIELD.get(ps_col)
            if not dto_field:
                return
            width = cls._PS_COLUMN_WIDTHS[ps_col]
            plan.append((ps_col, dto_field, width))
            used_columns.add(ps_col)

        # IDs.
        if request.process_id:
            add('pid')
        if request.parent_process_id:
            add('ppid')
        if request.process_group_id:
            add('pgid')

        # Users.
        if request.user_name:
            add('user')
        if request.user_id:
            add('uid')
        if request.real_user_name:
            add('ruser')
        if request.real_user_id:
            add('ruid')

        # Names and command line.
        if request.process_name:
            add('comm')
        if request.command_line:
            add('args')

        # CPU and memory.
        if request.cpu_usage_percent:
            add('%cpu')
        if request.memory_usage_percent:
            add('%mem')
        if request.cpu_process_time:
            add('cputime')
        if request.elapsed_since_start:
            add('etime')
        if request.started_at:
            add('lstart')

        # Status and terminal.
        if request.status:
            add('stat')
        if request.terminal:
            add('tty')

        # Scheduling and priority.
        if request.priority:
            add('pri')
        if request.nice_value:
            add('nice')
        if request.scheduler_class:
            add('cls')
        if request.scheduler_policy:
            add('policy')
        if request.realtime_priority:
            add('rtprio')

        # Memory.
        if request.virtual_memory_kb:
            add('vsz')
        if request.resident_memory_kb:
            add('rss')

        # CPU placement and cgroup.
        if request.current_cpu:
            add('psr')
        if request.cgroup_path:
            add('cgroup')

        # Threads and wait info.
        if request.threads:
            add('nlwp')
        if request.wait_channel:
            add('wchan')

        # Flags and faults.
        if request.kernel_flags:
            add('flags')
        if request.major_page_faults:
            add('maj_flt')
        if request.minor_page_faults:
            add('min_flt')

        # Session and thread group.
        if request.session_id:
            add('sid')
        if request.thread_group_id:
            add('tgid')

        # Ensure at least one column for ps correctness.
        if not plan:
            add('pid')

        return plan

    @classmethod
    def _build_ps_format(cls, plan: List[tuple]) -> str:
        """
        Build ps -o format string from plan.
        """
        parts: List[str] = []
        for ps_col, _dto_field, width in plan:
            parts.append(f'{ps_col}:{width}')
        return ','.join(parts)

    @classmethod
    def _run_ps(cls, ps_format: str) -> str:
        """
        Run ps command and return stdout as text.
        """
        try:
            proc = subprocess.run(
                ['ps', '-ww', '-eo', ps_format],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
        except Exception:
            return ''
        if proc.returncode != 0:
            return ''
        return proc.stdout or ''

    # --------------------------------------------------------------------------
    # --- PARSING AND CONVERTING DATA METHODS. ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _to_float(v: str) -> Optional[float]:
        """
        Convert string to float or return None.
        """
        try:
            return float(v.replace(',', '.'))
        except Exception:
            return None

    @staticmethod
    def _to_int(v: str) -> Optional[int]:
        """
        Convert string to int or return None.
        """
        try:
            return int(v, 10)
        except Exception:
            return None

    @classmethod
    def _parse_start_datetime(cls, dto: ProcessInfoDto) -> Optional[datetime]:
        """
        Parse start datetime from lstart/start fields.
        """
        s = dto.lstart or dto.start_time or dto.start
        if not s:
            return None
        text = str(s).strip()
        if not text:
            return None

        parts = text.split()
        if len(parts) < 5:
            return None

        # Expected: WEEKDAY MONTH DAY HH:MM:SS YEAR
        month_token = parts[1].lower()
        day_str = parts[2]
        time_str = parts[3]
        year_str = parts[4]

        month = cls._MONTHS.get(month_token)
        if not month:
            return None

        try:
            day = int(day_str)
            year = int(year_str)
            h_str, m_str, s_str = time_str.split(':')
            hour = int(h_str)
            minute = int(m_str)
            second = int(s_str)
        except Exception:
            return None

        try:
            return datetime(year, month, day, hour, minute, second)
        except Exception:
            return None

    @classmethod
    def _parse_fixed_width_line(cls, line: str, plan: List[tuple]) -> Dict[str, Optional[str]]:
        """
        Parse one fixed-width ps line into raw dict of strings.
        """
        result: Dict[str, Optional[str]] = {}
        pos = 0

        for idx, (_ps_col, dto_field, width) in enumerate(plan):
            if idx == len(plan) - 1:
                chunk = line[pos:]
            else:
                chunk = line[pos:pos + width]
            value = chunk.rstrip() or None
            result[dto_field] = value
            if idx != len(plan) - 1:
                pos += width + 1

        return result
    
    @classmethod
    def _convert_types(cls, row: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Convert raw string values to int/float where needed.
        """
        out: Dict[str, Any] = {}
        for key, value in row.items():
            if value is None:
                out[key] = None
                continue

            text = value.strip()
            if not text or text == '-':
                out[key] = None
                continue

            if key in cls._INT_FIELDS:
                out[key] = cls._to_int(text)
            elif key in cls._FLOAT_FIELDS:
                out[key] = cls._to_float(text)
            else:
                out[key] = text
        return out

    @classmethod
    def _parse_ps_output(cls, output: str, plan: List[tuple]) -> List[ProcessInfoDto]:
        """
        Parse ps command output into list of ProcessInfoDto.
        """
        lines = output.splitlines()
        if not lines or len(lines) < 2:
            return []

        data_lines = lines[1:]
        rows: List[Dict[str, Any]] = []

        for line in data_lines:
            if not line.strip():
                continue
            raw = cls._parse_fixed_width_line(line, plan)
            typed = cls._convert_types(raw)
            rows.append(typed)

        return ProcessInfoDto.list_from_dicts(rows)

    # --------------------------------------------------------------------------
    # --- MAPPING DTO -> ProcessInfo METHODS. ---
    # --------------------------------------------------------------------------

    @classmethod
    def _dto_to_process_info(cls, dto: ProcessInfoDto, request: ProcessInfoRequest) -> ProcessInfo:
        """
        Map ProcessInfoDto to ProcessInfo using field request.
        """
        d: Dict[str, Any] = {}

        # IDs
        if request.process_id:
            d[ProcessInfo.FIELD_PROCESS_ID] = dto.pid
        if request.parent_process_id:
            d[ProcessInfo.FIELD_PARENT_PROCESS_ID] = dto.ppid
        if request.process_group_id:
            d[ProcessInfo.FIELD_PROCESS_GROUP_ID] = dto.pgid

        # Users
        if request.user_name:
            d[ProcessInfo.FIELD_USER_NAME] = dto.user
        if request.user_id:
            d[ProcessInfo.FIELD_USER_ID] = dto.uid
        if request.real_user_name:
            d[ProcessInfo.FIELD_REAL_USER_NAME] = dto.ruser
        if request.real_user_id:
            d[ProcessInfo.FIELD_REAL_USER_ID] = dto.ruid

        # Names and command line
        if request.process_name:
            d[ProcessInfo.FIELD_PROCESS_NAME] = dto.comm
        if request.command_line:
            cmdline = dto.args or dto.cmd
            d[ProcessInfo.FIELD_COMMAND_LINE] = cmdline

        # CPU and memory
        if request.cpu_usage_percent:
            d[ProcessInfo.FIELD_CPU_USAGE_PERCENT] = dto.pcpu
        if request.memory_usage_percent:
            d[ProcessInfo.FIELD_MEMORY_USAGE_PERCENT] = dto.pmem
        if request.cpu_process_time:
            d[ProcessInfo.FIELD_CPU_PROCESS_TIME] = dto.cputime or dto.time
        if request.elapsed_since_start:
            d[ProcessInfo.FIELD_ELAPSED_SINCE_START] = dto.etime
        if request.started_at:
            d[ProcessInfo.FIELD_STARTED_AT] = cls._parse_start_datetime(dto)

        # Status and terminal
        if request.status:
            d[ProcessInfo.FIELD_STATUS] = dto.stat
        if request.terminal:
            d[ProcessInfo.FIELD_TERMINAL] = dto.tty

        # Scheduling and priority
        if request.priority:
            d[ProcessInfo.FIELD_PRIORITY] = dto.pri
        if request.nice_value:
            d[ProcessInfo.FIELD_NICE_VALUE] = dto.nice
        if request.scheduler_class:
            d[ProcessInfo.FIELD_SCHEDULER_CLASS] = dto.cls
        if request.scheduler_policy:
            d[ProcessInfo.FIELD_SCHEDULER_POLICY] = dto.policy
        if request.realtime_priority:
            d[ProcessInfo.FIELD_REALTIME_PRIORITY] = dto.rtprio

        # Memory
        if request.virtual_memory_kb:
            d[ProcessInfo.FIELD_VIRTUAL_MEMORY_KB] = dto.vsz
        if request.resident_memory_kb:
            d[ProcessInfo.FIELD_RESIDENT_MEMORY_KB] = dto.rss

        # CPU placement and cgroup
        if request.current_cpu:
            d[ProcessInfo.FIELD_CURRENT_CPU] = dto.psr
        if request.cgroup_path:
            d[ProcessInfo.FIELD_CGROUP_PATH] = dto.cgroup

        # Threads and wait info
        if request.threads:
            d[ProcessInfo.FIELD_THREADS] = dto.nlwp
        if request.wait_channel:
            d[ProcessInfo.FIELD_WAIT_CHANNEL] = dto.wchan

        # Flags and faults
        if request.kernel_flags:
            kernel_flags = dto.flags or (str(dto.f) if dto.f is not None else None)
            d[ProcessInfo.FIELD_KERNEL_FLAGS] = kernel_flags
        if request.major_page_faults:
            d[ProcessInfo.FIELD_MAJOR_PAGE_FAULTS] = dto.maj_flt
        if request.minor_page_faults:
            d[ProcessInfo.FIELD_MINOR_PAGE_FAULTS] = dto.min_flt

        # Session and thread group
        if request.session_id:
            d[ProcessInfo.FIELD_SESSION_ID] = dto.sid
        if request.thread_group_id:
            d[ProcessInfo.FIELD_THREAD_GROUP_ID] = dto.tgid

        return ProcessInfo.from_dict(d)

    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS. ---
    # --------------------------------------------------------------------------

    @classmethod
    def get_process_infos(cls, request: Optional[ProcessInfoRequest] = None) -> List[ProcessInfo]:
        """
        Get list of ProcessInfo objects for running processes.
        """
        if request is None:
            request = ProcessInfoRequest.default()

        plan = cls._build_ps_plan(request)
        ps_format = cls._build_ps_format(plan)
        output = cls._run_ps(ps_format)

        if not output:
            return []

        dto_rows = cls._parse_ps_output(output, plan)
        result: List[ProcessInfo] = []
        for dto in dto_rows:
            result.append(cls._dto_to_process_info(dto, request))
        return result
    
