from datetime import datetime
import subprocess
from typing import Any, ClassVar, Dict, List, Optional

from system_service.models.system.processes.process_info import ProcessInfo
from system_service.models.system.processes.process_info_dto import ProcessInfoDto
from system_service.models.system.processes.process_info_request import ProcessInfoRequest


class ProcessInfoResolver:
    """Static utility for collecting process information using ps command."""

    # PS columns names and their lengths in a specific order:
    _PS_COLUMNS: ClassVar[Dict[str, int]] = {
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

    # Map PS column -> ProcessInfoRequest.FIELD_*:
    _PS_COLUMNS_REQUEST_MAP: ClassVar[Dict[str, str]] = {
        'pid': ProcessInfoRequest.FIELD_PROCESS_ID,
        'ppid': ProcessInfoRequest.FIELD_PARENT_PROCESS_ID,
        'pgid': ProcessInfoRequest.FIELD_PROCESS_GROUP_ID,
        'uid': ProcessInfoRequest.FIELD_USER_ID,
        'ruid': ProcessInfoRequest.FIELD_REAL_USER_ID,
        'pri': ProcessInfoRequest.FIELD_PRIORITY,
        'priority': ProcessInfoRequest.FIELD_PRIORITY,
        'vsz': ProcessInfoRequest.FIELD_VIRTUAL_MEMORY_KB,
        'rss': ProcessInfoRequest.FIELD_RESIDENT_MEMORY_KB,
        'psr': ProcessInfoRequest.FIELD_CURRENT_CPU,
        'nlwp': ProcessInfoRequest.FIELD_THREADS,
        'thcount': ProcessInfoRequest.FIELD_THREADS,
        'flags': ProcessInfoRequest.FIELD_KERNEL_FLAGS,
        'f': ProcessInfoRequest.FIELD_KERNEL_FLAGS,
        'maj_flt': ProcessInfoRequest.FIELD_MAJOR_PAGE_FAULTS,
        'min_flt': ProcessInfoRequest.FIELD_MINOR_PAGE_FAULTS,
        'sid': ProcessInfoRequest.FIELD_SESSION_ID,
        'tgid': ProcessInfoRequest.FIELD_THREAD_GROUP_ID,
        'sess': ProcessInfoRequest.FIELD_SESSION_ID,
        '%cpu': ProcessInfoRequest.FIELD_CPU_USAGE_PERCENT,
        '%mem': ProcessInfoRequest.FIELD_MEMORY_USAGE_PERCENT,
        'stat': ProcessInfoRequest.FIELD_STATUS,
        'state': ProcessInfoRequest.FIELD_STATUS,
        'tty': ProcessInfoRequest.FIELD_TERMINAL,
        'nice': ProcessInfoRequest.FIELD_NICE_VALUE,
        'cls': ProcessInfoRequest.FIELD_SCHEDULER_CLASS,
        'policy': ProcessInfoRequest.FIELD_SCHEDULER_POLICY,
        'rtprio': ProcessInfoRequest.FIELD_REALTIME_PRIORITY,
        'user': ProcessInfoRequest.FIELD_USER_NAME,
        'ruser': ProcessInfoRequest.FIELD_REAL_USER_NAME,
        'cgroup': ProcessInfoRequest.FIELD_CGROUP_PATH,
        'wchan': ProcessInfoRequest.FIELD_WAIT_CHANNEL,
        'cputime': ProcessInfoRequest.FIELD_CPU_PROCESS_TIME,
        'time': ProcessInfoRequest.FIELD_CPU_PROCESS_TIME,
        'etime': ProcessInfoRequest.FIELD_ELAPSED_SINCE_START,
        'start': ProcessInfoRequest.FIELD_STARTED_AT,
        'start_time': ProcessInfoRequest.FIELD_STARTED_AT,
        'lstart': ProcessInfoRequest.FIELD_STARTED_AT,
        'comm': ProcessInfoRequest.FIELD_PROCESS_NAME,
        'args': ProcessInfoRequest.FIELD_COMMAND_LINE,
        'cmd': ProcessInfoRequest.FIELD_COMMAND_LINE,
    }

    # Map PS column -> ProcessInfoDto field name:
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

    # DTO fields that should be converted:
    _FIELDS_TO_CONVERT: ClassVar[Dict[str, str]] = {
        ProcessInfoDto.FIELD_PID: 'int',
        ProcessInfoDto.FIELD_PPID: 'int',
        ProcessInfoDto.FIELD_PGID: 'int',
        ProcessInfoDto.FIELD_UID: 'int',
        ProcessInfoDto.FIELD_RUID: 'int',
        ProcessInfoDto.FIELD_PRI: 'int',
        ProcessInfoDto.FIELD_VSZ: 'int',
        ProcessInfoDto.FIELD_RSS: 'int',
        ProcessInfoDto.FIELD_PSR: 'int',
        ProcessInfoDto.FIELD_NLWP: 'int',
        ProcessInfoDto.FIELD_F: 'int',
        ProcessInfoDto.FIELD_MAJ_FLT: 'int',
        ProcessInfoDto.FIELD_MIN_FLT: 'int',
        ProcessInfoDto.FIELD_SID: 'int',
        ProcessInfoDto.FIELD_TGID: 'int',
        ProcessInfoDto.FIELD_NICE: 'int',
        ProcessInfoDto.FIELD_PCPU: 'float',
        ProcessInfoDto.FIELD_PMEM: 'float'
    }

    # Month names for lstart parsing:
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
        'lis': 11,
        'gru': 12,
    }


    def __new__(cls, *args, **kwargs):
        """Prevent instantiation of this static utility class."""
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    
    # --------------------------------------------------------------------------
    # --- BUILD AND RUN PS COMMAND ---
    # --------------------------------------------------------------------------

    @classmethod
    def _get_enabled_columns(cls, request_dict: Dict[str, Any]) -> List[str]:
        """Get enabled ps columns in defined order based on request dict."""
        enabled: List[str] = []
        for col_name in cls._PS_COLUMNS.keys():
            req_field = cls._PS_COLUMNS_REQUEST_MAP.get(col_name)
            if not req_field:
                continue
            if not request_dict.get(req_field, False):
                continue

            # Avoid duplicating command line: prefer args over cmd.
            if col_name == 'cmd' and 'args' in enabled:
                continue

            enabled.append(col_name)
        return enabled

    @classmethod
    def _build_ps_cmd_args(cls, request_dict: Dict[str, Any]) -> List[str]:
        """Build ps -o arguments list based on request."""
        enabled_columns = cls._get_enabled_columns(request_dict)
        args: List[str] = []

        for col in enabled_columns:
            width = cls._PS_COLUMNS[col]
            args.append(f'{col}:{width}')
        return args

    @classmethod
    def _run_ps_cmd(cls, args: List[str]) -> str:
        """Run ps command and return stdout as text."""
        fmt = ','.join(args)
        cmd = ['ps', '-ww', '-eo', fmt]

        try:
            proc = subprocess.run(
                cmd,
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
    # --- PARSING AND CONVERSION DATA METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def _parse_ps_output_line(cls, line: str, enabled_columns: List[str]) -> Dict[str, Optional[str]]:
        """Parse one fixed-width ps line into raw dict of strings."""
        result: Dict[str, Optional[str]] = {}
        pos = 0
        last_index = len(enabled_columns) - 1

        for idx, col_name in enumerate(enabled_columns):
            width = cls._PS_COLUMNS[col_name]

            # For the last column and args/cmd take the rest of the line.
            if idx == last_index and col_name in ('args', 'cmd'):
                chunk = line[pos:]
            else:
                chunk = line[pos:pos + width]

            value = chunk.strip() or None

            dto_field = cls._PS_COLUMN_TO_DTO_FIELD.get(col_name)
            if dto_field:
                result[dto_field] = value

            pos += (width + 1)
        return result

    @staticmethod
    def _to_float(v: str) -> Optional[float]:
        """Convert string to float or return None."""
        try:
            return float(v.replace(',', '.'))
        except Exception:
            return None

    @staticmethod
    def _to_int(v: str) -> Optional[int]:
        """Convert string to int or return None."""
        try:
            return int(v, 10)
        except Exception:
            return None
    
    @classmethod
    def _convert_types(cls, row: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """Convert raw string values to int/float where needed."""
        out: Dict[str, Any] = {}

        for key, value in row.items():
            if value is None:
                out[key] = None
                continue

            text = value.strip()
            if not text:
                out[key] = None
                continue
            
            if key in cls._FIELDS_TO_CONVERT:
                target = cls._FIELDS_TO_CONVERT[key]

                if target == 'int':
                    out[key] = cls._to_int(text)
                elif target == 'float':
                    out[key] = cls._to_float(text)
                else:
                    out[key] = text
            else:
                out[key] = text
        return out

    @classmethod
    def _parse_ps_output(cls, output: str, request_dict: Dict[str, Any]) -> List[ProcessInfoDto]:
        """Parse ps command output into list of ProcessInfoDto."""
        lines = output.splitlines()
        if not lines or len(lines) < 2:
            return []

        enabled_columns = cls._get_enabled_columns(request_dict)
        data_lines = lines[1:]
        rows: List[Dict[str, Any]] = []

        for line in data_lines:
            if not line.strip():
                continue
            raw = cls._parse_ps_output_line(line, enabled_columns)
            typed = cls._convert_types(raw)
            rows.append(typed)

        return ProcessInfoDto.list_from_dicts(rows)
    
    # --------------------------------------------------------------------------
    # --- MAPPING DTO -> ProcessInfo ---
    # --------------------------------------------------------------------------

    @classmethod
    def _parse_lstart(cls, text: str) -> Optional[datetime]:
        """Parse lstart format 'Thu Nov 14 09:26:44 2025'."""
        parts = text.split()
        if len(parts) < 5:
            return None

        month_token = parts[1].lower()
        month = cls._MONTHS.get(month_token)
        if not month:
            return None

        try:
            day = int(parts[2])
            year = int(parts[4])
            h, m, s = parts[3].split(':')
            return datetime(year, month, day, int(h), int(m), int(s))
        except Exception:
            return None

    @classmethod
    def _parse_start_fallback(cls, text: str) -> Optional[datetime]:
        """Try to interpret ps 'start' or 'start_time' value."""
        text = (text or '').strip()
        if not text:
            return None

        # Time-like: HH:MM or HH:MM:SS
        if ':' in text:
            parts = text.split(':')
            try:
                if len(parts) == 2:
                    h, m = int(parts[0]), int(parts[1])
                    s = 0
                elif len(parts) == 3:
                    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                else:
                    return None
                now = datetime.now()
                return datetime(now.year, now.month, now.day, h, m, s)
            except Exception:
                return None

        # Date-like: 'Nov 13', 'Nov13', 'lis 13', 'lis13'
        tokens = text.split()
        if len(tokens) == 2:
            mon_token = tokens[0][:3].lower()
            day_str = tokens[1]
        else:
            mon_token = text[:3].lower()
            day_str = text[3:]

        month = cls._MONTHS.get(mon_token)
        if not month:
            return None

        try:
            day = int(day_str)
            now = datetime.now()
            return datetime(now.year, month, day, 0, 0, 0)
        except Exception:
            return None

    @classmethod
    def _parse_start_datetime(cls, dto: ProcessInfoDto) -> Optional[datetime]:
        """Parse start datetime with lstart -> start_time -> start fallback."""
        # 1. Most accurate format (e.g. 'Thu Nov 14 09:26:44 2025').
        if dto.lstart:
            dt = cls._parse_lstart(dto.lstart)
            if dt:
                return dt

        # 2. start_time: Can be 'lis13' or '13:02'
        if dto.start_time:
            dt = cls._parse_start_fallback(dto.start_time)
            if dt:
                return dt

        # 3. start: can be 'Nov 13' or '18:54:24'
        if dto.start:
            dt = cls._parse_start_fallback(dto.start)
            if dt:
                return dt

        return None

    @classmethod
    def _dto_to_process_info(cls, dto: ProcessInfoDto, request: ProcessInfoRequest) -> ProcessInfo:
        """Map ProcessInfoDto to ProcessInfo using field request."""
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
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def get_process_infos(cls, request: Optional[ProcessInfoRequest] = None) -> List[ProcessInfo]:
        """Get list of ProcessInfo for running processes."""
        if request is None:
            request = ProcessInfoRequest.default()

        request_dict = request.to_dict()
        ps_args = cls._build_ps_cmd_args(request_dict)
        output = cls._run_ps_cmd(ps_args)

        if not output:
            return []

        dto_rows = cls._parse_ps_output(output, request_dict)
        result: List[ProcessInfo] = []
        for dto in dto_rows:
            result.append(cls._dto_to_process_info(dto, request))
        return result