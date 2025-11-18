from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar, Dict, Optional, Type, TypeVar

from utils.models.public_model import PublicModel


T = TypeVar('T', bound='OSUserLoggedIn')


@dataclass
class OSUserLoggedIn(PublicModel):

    # --------------------------------------------------------------------------
    # --- FIELDS NAMES & CONFIGURATION ---
    # --------------------------------------------------------------------------

    FIELD_USER_NAME: ClassVar[str] = 'user_name'
    FIELD_TERMINAL_NAME: ClassVar[str] = 'terminal_name'
    FIELD_LOGGED_AT: ClassVar[str] = 'logged_at'
    FIELD_REMOTE_HOST: ClassVar[str] = 'remote_host'
    FIELD_IDLE_TIME: ClassVar[str] = 'idle_time'
    FIELD_JOB_CPU_TIME: ClassVar[str] = 'job_cpu_time'
    FIELD_PROCESS_CPU_TIME: ClassVar[str] = 'process_cpu_time'
    FIELD_SESSION_COMMAND: ClassVar[str] = 'session_command'
    FIELD_PROCESS_ID: ClassVar[str] = 'process_id'
    FIELD_SESSION_COMMENT: ClassVar[str] = 'session_comment'

    _DATE_TIME_FORMAT: ClassVar[str] = '%Y-%m-%d %H:%M'

    # --------------------------------------------------------------------------
    # --- DATA FIELDS ---
    # --------------------------------------------------------------------------

    user_name: str                          # login
    terminal_name: Optional[str]            # term (e.g., pts/0, tty1)
    logged_at: Optional[datetime]           # timestamp (YYYY-MM-DD HH:MM)
    remote_host: Optional[str]              # from (host or '-')
    idle_time: Optional[timedelta]          # idle/time ('?', '05:43', etc.)
    job_cpu_time: Optional[float]           # jcpu (in seconds)
    process_cpu_time: Optional[float]       # pcpu (in seconds)
    session_command: Optional[str]          # what (command/session)
    process_id: Optional[int]               # pid
    session_comment: Optional[str]          # comment (host in parentheses)

    # --------------------------------------------------------------------------
    # --- HELPER METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def _parse_dt(cls, s: Optional[str]) -> Optional[datetime]:
        if not s or not isinstance(s, str):
            return None
        s = s.strip()

        # expected 'YYYY-MM-DD HH:MM' (who -u).
        try:
            return datetime.strptime(s, cls._DATE_TIME_FORMAT)
        except Exception:
            return None

    @staticmethod
    def _parse_idle(s: Optional[str]) -> Optional[timedelta]:
        # who idle/time: examples '?', 'old', '05:43', '3days', '1:02', '00:00'.
        if not s or not isinstance(s, str):
            return None
        
        s = s.strip().lower()
        if s in ('?', '-', 'old'):
            return None
        
        # HH:MM or M:SS.
        if ':' in s and all(part.isdigit() for part in s.split(':')):
            parts = [int(p) for p in s.split(':')]
            if len(parts) == 2:
                h, m = parts
                return timedelta(hours=h, minutes=m)
            if len(parts) == 3:
                h, m, sec = parts
                return timedelta(hours=h, minutes=m, seconds=sec)
            return None
        
        # forms like '5.53m' or '5m53s' are uncommon in idle, ignore.
        return None

    @staticmethod
    def _parse_cpu_secs(s: Optional[Any]) -> Optional[float]:
        # w -h jcpu/pcpu examples: '0.00s', '5.53m', '1:02', '-', ''.
        if s is None:
            return None
        
        if isinstance(s, (int, float)):
            return float(s)
        
        if not isinstance(s, str):
            return None
        
        txt = s.strip().lower()
        if txt in ('', '-', '?'):
            return None
        
        # 1) 12.34s → seconds.
        if txt.endswith('s'):
            try:
                return float(txt[:-1])
            except ValueError:
                return None
            
        # 2) 5.53m → minutes.
        if txt.endswith('m'):
            try:
                return float(txt[:-1]) * 60.0
            except ValueError:
                return None
            
        # 3) HH:MM[:SS].
        if ':' in txt and all(p.isdigit() for p in txt.split(':')):
            try:
                parts = [int(p) for p in txt.split(':')]
                if len(parts) == 2:
                    h, m = parts
                    return float(h * 3600 + m * 60)
                if len(parts) == 3:
                    h, m, sec = parts
                    return float(h * 3600 + m * 60 + sec)
            except Exception:
                return None
        return None

    @staticmethod
    def _parse_int(v: Any) -> Optional[int]:
        try:
            return int(v) if v not in (None, '', '-') else None
        except Exception:
            return None

    @classmethod
    def _fmt_dt(cls, dt: Optional[datetime]) -> Optional[str]:
        if not dt:
            return None
        return dt.strftime(cls._DATE_TIME_FORMAT)

    @staticmethod
    def _fmt_td(td: Optional[timedelta]) -> Optional[str]:
        if not td:
            return None
        total = int(td.total_seconds())
        days, rem = divmod(total, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        if days > 0:
            return f'{days}-{h:02d}:{m:02d}:{s:02d}'
        return f'{h:02d}:{m:02d}:{s:02d}'

    # --------------------------------------------------------------------------
    # --- SERIALIZATION ---
    # --------------------------------------------------------------------------

    @classmethod
    def from_dict(cls: Type[T], d: Dict[str, Any]) -> OSUserLoggedIn:
        return cls(
            user_name=d.get(cls.FIELD_USER_NAME),
            terminal_name=d.get(cls.FIELD_TERMINAL_NAME),
            logged_at=cls._parse_dt(d.get(cls.FIELD_LOGGED_AT)),
            remote_host=d.get(cls.FIELD_REMOTE_HOST),
            idle_time=cls._parse_idle(d.get(cls.FIELD_IDLE_TIME)),
            job_cpu_time=cls._parse_cpu_secs(d.get(cls.FIELD_JOB_CPU_TIME)),
            process_cpu_time=cls._parse_cpu_secs(d.get(cls.FIELD_PROCESS_CPU_TIME)),
            session_command=d.get(cls.FIELD_SESSION_COMMAND),
            process_id=cls._parse_int(d.get(cls.FIELD_PROCESS_ID)),
            session_comment=d.get(cls.FIELD_SESSION_COMMENT),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_USER_NAME: self.user_name,
            self.FIELD_TERMINAL_NAME: self.terminal_name,
            self.FIELD_LOGGED_AT: self._fmt_dt(self.logged_at),
            self.FIELD_REMOTE_HOST: self.remote_host,
            self.FIELD_IDLE_TIME: self._fmt_td(self.idle_time),
            self.FIELD_JOB_CPU_TIME: self.job_cpu_time,
            self.FIELD_PROCESS_CPU_TIME: self.process_cpu_time,
            self.FIELD_SESSION_COMMAND: self.session_command,
            self.FIELD_PROCESS_ID: self.process_id,
            self.FIELD_SESSION_COMMENT: self.session_comment,
        }

    # --------------------------------------------------------------------------
    # --- SWAGGER SCHEMATICS ---
    # --------------------------------------------------------------------------

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_USER_NAME: {'type': 'string', 'example': 'root'},
                cls.FIELD_TERMINAL_NAME: {'type': ['string', 'null'], 'example': 'tty1'},
                cls.FIELD_LOGGED_AT: {'type': 'string', 'example': 'YYYY-MM-DD HH:MM'},
                cls.FIELD_REMOTE_HOST: {'type': ['string', 'null'], 'example': '10.6.0.1'},
                cls.FIELD_IDLE_TIME: {'type': ['string', 'null'], 'example': 'HH:MM'},
                cls.FIELD_JOB_CPU_TIME: {'type': ['number', 'null'], 'example': 0.08},
                cls.FIELD_PROCESS_CPU_TIME: {'type': ['number', 'null'], 'example': 0.08},
                cls.FIELD_SESSION_COMMAND: {'type': ['string', 'null'], 'example': '-bash'},
                cls.FIELD_PROCESS_ID: {'type': ['integer', 'null'], 'example': 964},
                cls.FIELD_SESSION_COMMENT: {'type': ['integer', 'null'], 'example': '(10.6.0.1)'},
            },
            'required': [cls.FIELD_USER_NAME, cls.FIELD_LOGGED_AT],
            'additionalProperties': False,
        }