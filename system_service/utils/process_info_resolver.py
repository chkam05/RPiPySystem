from datetime import datetime, timedelta
import subprocess
from typing import Any, Dict, Iterable, List, Optional, Union

from system_service.models.system.process_info import ProcessInfo
from system_service.models.system.process_info_dto import ProcessInfoDto
from system_service.models.system.process_info_request import ProcessInfoRequest


class ProcessInfoResolver:
    """Run ps(1), parse rows into ProcessInfoDto, then map to ProcessInfo."""

    # Month names/abbreviations map for parsing lstart.
    _MONTHS = {
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
    
    # Weekday names (ignored, but must be recognized).
    _WEEKDAYS = {
        'mon',
        'tue',
        'wed',
        'thu',
        'fri',
        'sat',
        'sun',
        'pon',
        'wto',
        'śro',
        'sro',
        'czw',
        'pią',
        'pia',
        'sob',
        'nie',
    }

    # ps columns (full superset) in stable canonical order (without 'args'/'cmd').
    _CANONICAL_PREFIX: List[str] = [
        'pid',
        'ppid',
        'pgid',
        'user',
        'uid',
        'ruser',
        'ruid',
        'comm',
        '%cpu',
        '%mem',
        'cputime',
        'etime',
        'time',
        'start',
        'start_time'
    ]

    _CANONICAL_AFTER_LSTART: List[str] = [
        'stat',
        'state',
        'tty',
        'pri',
        'priority',
        'nice',
        'cls',
        'policy',
        'rtprio',
        'vsz',
        'rss',
        'psr',
        'cpu',
        'cgroup',
        'nlwp',
        'thcount',
        'wchan',
        'flags',
        'f',
        'maj_flt',
        'min_flt',
        'sid',
        'tgid',
        'sess'
    ]

    # Subset safe to split on whitespace (when 'args' or 'cmd' is last).
    _FIXED_BEFORE_ARGS: List[str] = [
        'pid',
        'ppid',
        'pgid',
        'user',
        'uid',
        'ruser',
        'ruid',
        'comm',
        '%cpu',
        '%mem',
        'cputime',
        'etime',
        'time',
        'start', 
        'start_time',
        'lstart',
        'stat',
        'state',
        'tty',
        'pri',
        'priority',
        'nice',
        'cls',
        'policy',
        'rtprio',
        'vsz',
        'rss',
        'psr',
        'cpu',
        'cgroup',
        'nlwp',
        'thcount',
        'wchan',
        'flags',
        'f',
        'maj_flt',
        'min_flt',
        'sid',
        'tgid',
        'sess',
    ]

    # Safe field separator for ps output (unit separator, U+001F) – kept for reference.
    _SEP: str = '\x1f'


    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation of this static utility class.
        """
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    
    # --------------------------------------------------------------------------
    # --- HELPER FUNCTIONS FOR PARSING ---
    # --------------------------------------------------------------------------

    @classmethod
    def _select_command_line(cls, dto: ProcessInfoDto) -> Optional[str]:
        """
        Return args or cmd depending on availability.
        """
        def clean(x: Optional[str]) -> Optional[str]:
            if x is None:
                return None
            x = x.strip()
            return None if x in ('-', '') else x
        return clean(dto.args) or clean(dto.cmd)

    @classmethod
    def _num(cls, v: Optional[Union[str, float, int]]) -> Optional[float]:
        """
        Convert numeric-like values into float or None.
        """
        if v is None or v == '-':
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @classmethod
    def _parse_duration(cls, s: Optional[str]) -> Optional[timedelta]:
        """
        Convert duration-like ps values into timedelta.
        """
        if not s or s == '-':
            return None
        s = s.strip()

        days = 0
        if '-' in s:
            # Format D-HH:MM:SS.
            day_part, s = s.split('-', 1)
            try:
                days = int(day_part)
            except ValueError:
                return None

        parts = s.split(':')
        try:
            if len(parts) == 3:
                h, m, sec = map(int, parts)
            elif len(parts) == 2:
                h, m, sec = 0, int(parts[0]), int(parts[1])
            else:
                return None
        except ValueError:
            return None

        return timedelta(days=days, hours=h, minutes=m, seconds=sec)

    @classmethod
    def _parse_started_at(cls, dto: ProcessInfoDto) -> Optional[datetime]:
        """
        Parse full datetime from lstart field.
        """
        if dto.lstart and dto.lstart != '-':
            dt = cls._parse_lstart_like(dto.lstart)
            if dt:
                return dt
        return None

    @classmethod
    def _parse_lstart_like(cls, text: str) -> Optional[datetime]:
        """
        Parse lstart formatted string '<dow> <mon> <day> HH:MM:SS YYYY>'.
        """
        if not text:
            return None

        parts = [p for p in text.split() if p]
        normalized = [cls._norm_token(p) for p in parts]

        if len(normalized) < 5:
            return None

        try:
            year = int(normalized[-1])
        except ValueError:
            return None

        # Identify time token (HH:MM:SS).
        time_val = next((p for p in normalized if p.count(':') == 2), None)
        if not time_val:
            return None

        # Identify month.
        mon_idx = None
        for i, token in enumerate(normalized):
            if token in cls._MONTHS:
                mon_idx = i
                break
        if mon_idx is None:
            return None

        try:
            month = cls._MONTHS[normalized[mon_idx]]
        except KeyError:
            return None

        # Day follows month.
        try:
            day = int(normalized[mon_idx + 1])
        except (ValueError, IndexError):
            return None

        try:
            h, m, s = map(int, time_val.split(':'))
        except ValueError:
            return None

        try:
            return datetime(year, month, day, h, m, s)
        except Exception:
            return None

    @classmethod
    def _norm_token(cls, t: str) -> str:
        """
        Normalize token by removing diacritics and lowercasing.
        """
        return t.strip().lower().translate(str.maketrans({
            'ś': 's', 'ł': 'l', 'ó': 'o', 'ą': 'a',
            'ę': 'e', 'ż': 'z', 'ź': 'z', 'ć': 'c', 'ń': 'n'
        }))

    # --------------------------------------------------------------------------
    # --- LOW-LEVEL MAPPING / CASTING HELPERS ---
    # --------------------------------------------------------------------------

    @classmethod
    def _map_and_cast(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map raw ps keys to DTO keys and cast integers where safe.
        """
        mapped: Dict[str, Any] = {}
        for k, v in raw.items():
            if k == '%cpu':
                mapped['pcpu'] = v
            elif k == '%mem':
                mapped['pmem'] = v
            else:
                mapped[k] = v

        int_fields = {
            'pid', 'ppid', 'pgid', 'uid', 'ruid', 'pri', 'priority', 'nice',
            'rtprio', 'vsz', 'rss', 'psr', 'cpu', 'nlwp', 'thcount',
            'maj_flt', 'min_flt', 'sid', 'tgid', 'sess'
        }
        for key in int_fields:
            val = mapped.get(key)
            if val not in (None, '-', ''):
                try:
                    mapped[key] = int(val)
                except ValueError:
                    pass
        return mapped

    @classmethod
    def _safe_int(cls, v: Any) -> Optional[int]:
        """
        Convert to int or return None.
        """
        try:
            return int(v) if v not in (None, '', '-') else None
        except Exception:
            return None

    # --------------------------------------------------------------------------
    # --- COLUMN SELECTION BASED ON ProcessInfoRequest ---
    # --------------------------------------------------------------------------

    @classmethod
    def _columns_for_request(cls, request: ProcessInfoRequest, last_wide: Optional[str]) -> List[str]:
        """Build ordered ps column list driven by ProcessInfoRequest."""
        # Always include pid to identify and merge rows.
        selected: set[str] = {'pid'}

        # Map ProcessInfoRequest booleans to ps fields.
        if request.parent_process_id: selected.add('ppid')
        if request.process_group_id: selected.add('pgid')

        if request.user_name: selected.add('user')
        if request.user_id: selected.add('uid')
        if request.real_user_name: selected.add('ruser')
        if request.real_user_id: selected.add('ruid')

        if request.process_name: selected.add('comm')

        # command_line handled by last_wide ('args' / 'cmd'); but if requested, we include none of them here
        # and let last_wide append them at the end.
        # CPU/mem usage
        if request.cpu_usage_percent: selected.add('%cpu')
        if request.memory_usage_percent: selected.add('%mem')

        # Durations
        if request.cpu_process_time:
            selected.add('cputime')
            selected.add('time')  # keep both, resolver prefers cputime then time
        if request.elapsed_since_start: selected.add('etime')

        # Datetime
        if request.started_at:
            selected.add('lstart')  # full start datetime; far safer than parsing 'start'

        if request.status: selected.add('stat')
        if request.terminal: selected.add('tty')

        if request.priority: selected.add('pri')
        if request.nice_value: selected.add('nice')
        if request.scheduler_class: selected.add('cls')
        if request.scheduler_policy: selected.add('policy')
        if request.realtime_priority: selected.add('rtprio')

        if request.virtual_memory_kb: selected.add('vsz')
        if request.resident_memory_kb: selected.add('rss')

        if request.current_cpu: selected.add('psr')
        if request.cgroup_path: selected.add('cgroup')
        if request.threads: selected.add('nlwp')
        if request.wait_channel: selected.add('wchan')
        if request.kernel_flags:
            selected.add('flags')
            selected.add('f')
        if request.major_page_faults: selected.add('maj_flt')
        if request.minor_page_faults: selected.add('min_flt')
        if request.session_id: selected.add('sid')
        if request.thread_group_id: selected.add('tgid')

        # Build ordered list: prefix ∩ selected, then optional lstart, then after_lstart ∩ selected, finally last_wide.
        columns: List[str] = []
        for k in cls._CANONICAL_PREFIX:
            if k in selected:
                columns.append(k)
        has_lstart = 'lstart' in selected
        if has_lstart:
            columns.append('lstart')
        for k in cls._CANONICAL_AFTER_LSTART:
            if k in selected:
                columns.append(k)
        if last_wide:
            columns.append(last_wide)
        return columns

    # --------------------------------------------------------------------------
    # --- BUILD AND EXEC ps(1). ---
    # --------------------------------------------------------------------------

    @classmethod
    def _build_ps_cmd_with_columns(cls, columns: List[str]) -> List[str]:
        """
        Build ps command with provided columns (last column may be wide).
        """
        fmt = ','.join(columns)
        return ['ps', '-ww', '-eo', fmt, '--no-headers']

    @classmethod
    def _run_ps_generic(cls, cmd: List[str]) -> List[str]:
        """
        Execute ps command and return each non-empty output line.
        """
        try:
            output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f'ps failed with exit code {e.returncode}: {e.output.strip()}') from e
        return [line.rstrip('\n') for line in output.splitlines() if line.strip() != '']
    
    # --------------------------------------------------------------------------
    # -- GENERIC PARSER FOR VARIABLE COLUMN SETS (last_wide optional) --
    # --------------------------------------------------------------------------

    @classmethod
    def _parse_line_with_columns(cls, line: str, columns: List[str]) -> Optional[Dict[str, Any]]:
        """
        Parse a ps line for a specific ordered column set; last column may be wide.
        """
        tokens = line.split()
        if not tokens or not columns:
            return None

        last_wide = columns[-1] if columns[-1] in ('args', 'cmd') else None
        has_lstart = 'lstart' in columns

        # Split logical layout
        if has_lstart:
            idx_l = columns.index('lstart')
            prefix_cols = columns[:idx_l]       # before lstart.
            after_cols = columns[idx_l + 1:]    # after lstart (may include last_wide).
        else:
            prefix_cols = [c for c in columns if c not in ('args', 'cmd')]
            after_cols = [c for c in columns if c not in prefix_cols]

        # If wide is at the end, fixed-after = everything in after_cols except that wide.
        after_fixed = after_cols[:-1] if (last_wide and after_cols and after_cols[-1] == last_wide) else after_cols

        raw: Dict[str, Any] = {}
        pos = 0

        # 1) consume prefix columns from the left.
        if len(tokens) < len(prefix_cols):
            return None
        for key in prefix_cols:
            raw[key] = tokens[pos]
            pos += 1

        # 2) consume lstart (exactly 5 tokens) from the left.
        if has_lstart:
            if len(tokens) < pos + 5:
                return None
            lstart_tokens = tokens[pos:pos + 5]
            raw['lstart'] = ' '.join(lstart_tokens)
            pos += 5

        # 3) consume fixed-after columns sequentially from the left.
        if len(tokens) < pos + len(after_fixed):
            return None
        for key in after_fixed:
            raw[key] = tokens[pos]
            pos += 1

        # 4) the rest (if any) belongs to the wide last column at the very end.
        if last_wide:
            raw[last_wide] = ' '.join(tokens[pos:]) if pos < len(tokens) else None

        return cls._map_and_cast(raw)

    # --------------------------------------------------------------------------
    # --- DTO ProcessInfo CONVERSION ---
    # --------------------------------------------------------------------------

    @classmethod
    def _from_dto(cls, dto: ProcessInfoDto) -> ProcessInfo:
        """
        Convert ProcessInfoDto into simplified ProcessInfo.
        """
        command_line = cls._select_command_line(dto)
        started_at = cls._parse_started_at(dto)
        cpu_time = cls._parse_duration(dto.cputime or dto.time)
        elapsed = cls._parse_duration(dto.etime)

        # Merge flags: prefer flags, fallback to f.
        flags = dto.flags if dto.flags not in (None, '-', '') else dto.f
        flags = None if flags in (None, '-', '') else str(flags)

        return ProcessInfo(
            process_id=dto.pid,
            parent_process_id=dto.ppid,
            process_group_id=dto.pgid,
            user_name=dto.user,
            user_id=dto.uid,
            real_user_name=dto.ruser,
            real_user_id=dto.ruid,
            process_name=dto.comm,
            command_line=command_line,
            cpu_usage_percent=cls._num(dto.pcpu),
            memory_usage_percent=cls._num(dto.pmem),
            cpu_process_time=cpu_time,
            elapsed_since_start=elapsed,
            started_at=started_at,
            status=dto.stat,
            terminal=dto.tty,
            priority=dto.pri,
            nice_value=dto.nice,
            scheduler_class=dto.cls,
            scheduler_policy=dto.policy,
            realtime_priority=None if dto.rtprio in (None, '-', '') else str(dto.rtprio),
            virtual_memory_kb=dto.vsz,
            resident_memory_kb=dto.rss,
            current_cpu=dto.psr,
            cgroup_path=dto.cgroup,
            threads=dto.nlwp,
            wait_channel=(None if dto.wchan in (None, '-', '') else dto.wchan),
            kernel_flags=flags,
            major_page_faults=dto.maj_flt,
            minor_page_faults=dto.min_flt,
            session_id=dto.sid,
            thread_group_id=dto.tgid,
        )

    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def get_process_infos(cls, request: Optional[ProcessInfoRequest] = None) -> List[ProcessInfo]:
        """
        Return a list of ProcessInfo objects collected from the system.
        """
        dtos = cls.get_process_info_dtos(request=request)
        return [cls._from_dto(dto) for dto in dtos]

    @classmethod
    def get_process_info_dtos(cls, request: Optional[ProcessInfoRequest] = None) -> List[ProcessInfoDto]:
        """
        Return a list of ProcessInfoDto objects based on ps output.
        """
        req = request or ProcessInfoRequest.default()
        rows_by_pid: Dict[int, Dict[str, Any]] = {}

        # If command line is requested, run two passes: args-last and cmd-last.
        if req.command_line:
            cols_args = cls._columns_for_request(req, last_wide='args')
            cols_cmd = cls._columns_for_request(req, last_wide='cmd')

            lines_args = cls._run_ps_generic(cls._build_ps_cmd_with_columns(cols_args))
            rows_args = [r for r in (cls._parse_line_with_columns(ln, cols_args) for ln in lines_args) if r is not None]

            lines_cmd = cls._run_ps_generic(cls._build_ps_cmd_with_columns(cols_cmd))
            rows_cmd = [r for r in (cls._parse_line_with_columns(ln, cols_cmd) for ln in lines_cmd) if r is not None]

            for r in rows_args:
                pid = cls._safe_int(r.get('pid'))
                if pid is not None:
                    rows_by_pid[pid] = r
            for r in rows_cmd:
                pid = cls._safe_int(r.get('pid'))
                if pid is None:
                    continue
                base = rows_by_pid.get(pid)
                if base is None:
                    rows_by_pid[pid] = r
                else:
                    if r.get('cmd') not in (None, ''):
                        base['cmd'] = r['cmd']
        else:
            # Single pass with only requested fixed columns (no wide last field).
            cols = cls._columns_for_request(req, last_wide=None)
            lines = cls._run_ps_generic(cls._build_ps_cmd_with_columns(cols))
            for ln in lines:
                r = cls._parse_line_with_columns(ln, cols)
                if r is None:
                    continue
                pid = cls._safe_int(r.get('pid'))
                if pid is not None:
                    rows_by_pid[pid] = r

        return [ProcessInfoDto.from_dict(row) for row in rows_by_pid.values()]