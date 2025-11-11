from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional


@dataclass
class ProcessInfoDto:
    # --- Field-name constants ---
    FIELD_PID: ClassVar[str] = 'pid'
    FIELD_PPID: ClassVar[str] = 'ppid'
    FIELD_PGID: ClassVar[str] = 'pgid'
    FIELD_USER: ClassVar[str] = 'user'
    FIELD_UID: ClassVar[str] = 'uid'
    FIELD_RUSER: ClassVar[str] = 'ruser'
    FIELD_RUID: ClassVar[str] = 'ruid'
    FIELD_COMM: ClassVar[str] = 'comm'
    FIELD_ARGS: ClassVar[str] = 'args'
    FIELD_CMD: ClassVar[str] = 'cmd'
    FIELD_PCPU: ClassVar[str] = 'pcpu'
    FIELD_PMEM: ClassVar[str] = 'pmem'
    FIELD_CPUTIME: ClassVar[str] = 'cputime'
    FIELD_ETIME: ClassVar[str] = 'etime'
    FIELD_TIME: ClassVar[str] = 'time'
    FIELD_START: ClassVar[str] = 'start'
    FIELD_START_TIME: ClassVar[str] = 'start_time'
    FIELD_LSTART: ClassVar[str] = 'lstart'
    FIELD_STAT: ClassVar[str] = 'stat'
    FIELD_STATE: ClassVar[str] = 'state'
    FIELD_TTY: ClassVar[str] = 'tty'
    FIELD_PRI: ClassVar[str] = 'pri'
    FIELD_PRIORITY: ClassVar[str] = 'priority'
    FIELD_NICE: ClassVar[str] = 'nice'
    FIELD_CLS: ClassVar[str] = 'cls'
    FIELD_POLICY: ClassVar[str] = 'policy'
    FIELD_RTPRIO: ClassVar[str] = 'rtprio'
    FIELD_VSZ: ClassVar[str] = 'vsz'
    FIELD_RSS: ClassVar[str] = 'rss'
    FIELD_PSR: ClassVar[str] = 'psr'
    FIELD_CPU: ClassVar[str] = 'cpu'
    FIELD_CGROUP: ClassVar[str] = 'cgroup'
    FIELD_NLWP: ClassVar[str] = 'nlwp'
    FIELD_THCOUNT: ClassVar[str] = 'thcount'
    FIELD_WCHAN: ClassVar[str] = 'wchan'
    FIELD_FLAGS: ClassVar[str] = 'flags'
    FIELD_F: ClassVar[str] = 'f'
    FIELD_MAJ_FLT: ClassVar[str] = 'maj_flt'
    FIELD_MIN_FLT: ClassVar[str] = 'min_flt'
    FIELD_SID: ClassVar[str] = 'sid'
    FIELD_TGID: ClassVar[str] = 'tgid'
    FIELD_SESS: ClassVar[str] = 'sess'

    # --- Fields ---

    pid: Optional[int]          # Process ID (unique identifier in the system).
    ppid: Optional[int]         # Parent process ID.
    pgid: Optional[int]         # Process group ID (group of processes with a common leader (e.g. pipelines in the shell)).
    user: Optional[str]         # Effective user of the process (who is the owner after permission changes).
    uid: Optional[int]          # Effective user ID.
    ruser: Optional[str]        # Current user (the one who started the process).
    ruid: Optional[int]         # Current user ID.
    comm: Optional[str]         # The name of the process (usually the basename of the program, with no arguments).
    args: Optional[str]         # The full command line of the given process, including arguments.
    cmd: Optional[str]          # Alias args.
    pcpu: Optional[float]       # Percentage of CPU usage calculated by ps.
    pmem: Optional[float]       # Percentage of RAM usage (based on RSS vs. available memory).
    cputime: Optional[str]      # Total CPU usage time by the process, (user+system).
    etime: Optional[str]        # Time since process start (from creation to now).
    time: Optional[str]         # Alias to cputime.
    start: Optional[str]        # Shortened start-up time (different format depending on how long the process runs).
    start_time: Optional[str]   # Process start time.
    lstart: Optional[str]       # Full date/time of the process start (human-readable).
    stat: Optional[str]         # Process status + additional flags.
    state: Optional[str]        # Basic process state.
    tty: Optional[str]          # Terminal assigned to the process.
    pri: Optional[int]          # Kernel process priority.
    priority: Optional[str]     # Alias ​​or priority conversion value.
    nice: Optional[int]         # Nice value adjustable by user.
    cls: Optional[str]          # Scheduler class.
    policy: Optional[str]       # Policy scheduling, scheduler type.
    rtprio: Optional[str]       # Real-Time priority (when scheduler is FIFO/RR).
    vsz: Optional[int]          # Process virtual memory size (KB).
    rss: Optional[int]          # Resident Set Size (actual memory in RAM (KB)).
    psr: Optional[int]          # The CPU number on which the process is currently executing.
    cpu: Optional[str]          # Alias ​​or internal statistics.
    cgroup: Optional[str]       # Cgroup assigned to the process (control group path in the system).
    nlwp: Optional[int]         # Number of LightWeight Processes (number of threads).
    thcount: Optional[str]      # Alias to nlwp.
    wchan: Optional[str]        # Symbolic name of the kernel function where the process waits ("wait channel").
    flags: Optional[str]        # Kernel flags of the process (in hexadecimal or decimal format).
    f: Optional[int]            # Legacy flag format (simplified integer value for reading flags).
    maj_flt: Optional[int]      # Major page faults (number of “large” page faults that required I/O).
    min_flt: Optional[int]      # Minor page faults (“small” page faults that did not require I/O).
    sid: Optional[int]          # Session ID - session leader (i.e. terminal session ID).
    tgid: Optional[int]         # Thread Group ID (same as the PID of the main process in a multithreaded application).
    sess: Optional[str]         # Alias ​​name session ID.

    # --- Packaging methods ---

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> 'ProcessInfoDto':
        return cls(
            pid=d.get(cls.FIELD_PID),
            ppid=d.get(cls.FIELD_PPID),
            pgid=d.get(cls.FIELD_PGID),
            user=d.get(cls.FIELD_USER),
            uid=d.get(cls.FIELD_UID),
            ruser=d.get(cls.FIELD_RUSER),
            ruid=d.get(cls.FIELD_RUID),
            comm=d.get(cls.FIELD_COMM),
            args=d.get(cls.FIELD_ARGS),
            cmd=d.get(cls.FIELD_CMD),
            pcpu=d.get(cls.FIELD_PCPU),
            pmem=d.get(cls.FIELD_PMEM),
            cputime=d.get(cls.FIELD_CPUTIME),
            etime=d.get(cls.FIELD_ETIME),
            time=d.get(cls.FIELD_TIME),
            start=d.get(cls.FIELD_START),
            start_time=d.get(cls.FIELD_START_TIME),
            lstart=d.get(cls.FIELD_LSTART),
            stat=d.get(cls.FIELD_STAT),
            state=d.get(cls.FIELD_STATE),
            tty=d.get(cls.FIELD_TTY),
            pri=d.get(cls.FIELD_PRI),
            priority=d.get(cls.FIELD_PRIORITY),
            nice=d.get(cls.FIELD_NICE),
            cls=d.get(cls.FIELD_CLS),
            policy=d.get(cls.FIELD_POLICY),
            rtprio=d.get(cls.FIELD_RTPRIO),
            vsz=d.get(cls.FIELD_VSZ),
            rss=d.get(cls.FIELD_RSS),
            psr=d.get(cls.FIELD_PSR),
            cpu=d.get(cls.FIELD_CPU),
            cgroup=d.get(cls.FIELD_CGROUP),
            nlwp=d.get(cls.FIELD_NLWP),
            thcount=d.get(cls.FIELD_THCOUNT),
            wchan=d.get(cls.FIELD_WCHAN),
            flags=d.get(cls.FIELD_FLAGS),
            f=d.get(cls.FIELD_F),
            maj_flt=d.get(cls.FIELD_MAJ_FLT),
            min_flt=d.get(cls.FIELD_MIN_FLT),
            sid=d.get(cls.FIELD_SID),
            tgid=d.get(cls.FIELD_TGID),
            sess=d.get(cls.FIELD_SESS)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            self.FIELD_PID: self.pid,
            self.FIELD_PPID: self.ppid,
            self.FIELD_PGID: self.pgid,
            self.FIELD_USER: self.user,
            self.FIELD_UID: self.uid,
            self.FIELD_RUSER: self.ruser,
            self.FIELD_RUID: self.ruid,
            self.FIELD_COMM: self.comm,
            self.FIELD_ARGS: self.args,
            self.FIELD_CMD: self.cmd,
            self.FIELD_PCPU: self.pcpu,
            self.FIELD_PMEM: self.pmem,
            self.FIELD_CPUTIME: self.cputime,
            self.FIELD_ETIME: self.etime,
            self.FIELD_TIME: self.time,
            self.FIELD_START: self.start,
            self.FIELD_START_TIME: self.start_time,
            self.FIELD_LSTART: self.lstart,
            self.FIELD_STAT: self.stat,
            self.FIELD_STATE: self.state,
            self.FIELD_TTY: self.tty,
            self.FIELD_PRI: self.pri,
            self.FIELD_PRIORITY: self.priority,
            self.FIELD_NICE: self.nice,
            self.FIELD_CLS: self.cls,
            self.FIELD_POLICY: self.policy,
            self.FIELD_RTPRIO: self.rtprio,
            self.FIELD_VSZ: self.vsz,
            self.FIELD_RSS: self.rss,
            self.FIELD_PSR: self.psr,
            self.FIELD_CPU: self.cpu,
            self.FIELD_CGROUP: self.cgroup,
            self.FIELD_NLWP: self.nlwp,
            self.FIELD_THCOUNT: self.thcount,
            self.FIELD_WCHAN: self.wchan,
            self.FIELD_FLAGS: self.flags,
            self.FIELD_F: self.f,
            self.FIELD_MAJ_FLT: self.maj_flt,
            self.FIELD_MIN_FLT: self.min_flt,
            self.FIELD_SID: self.sid,
            self.FIELD_TGID: self.tgid,
            self.FIELD_SESS: self.sess
        }

    def to_public(self) -> Dict[str, Any]:
        return self.to_dict()

    # --- Bulk helpers ---

    @classmethod
    def list_from_dicts(cls, rows: List[Dict[str, Any]]) -> List['ProcessInfoDto']:
        return [cls.from_dict(r) for r in (rows or [])]

    @staticmethod
    def list_to_dicts(items: List['ProcessInfoDto']) -> List[Dict[str, Any]]:
        return [i.to_public() for i in (items or [])]

    @classmethod
    def list_to_public(cls, items: List['ProcessInfoDto']) -> List[Dict[str, Any]]:
        return cls.list_to_dicts(items)

    # --- Schema methods ---

    @classmethod
    def schema_public(cls) -> Dict[str, Any]:
        return {
            'type': 'object',
            'properties': {
                cls.FIELD_PID: {'type': ['integer', 'null'], 'example': 471586},
                cls.FIELD_PPID: {'type': ['integer', 'null'], 'example': 471366},
                cls.FIELD_PGID: {'type': ['integer', 'null'], 'example': 471586},
                cls.FIELD_USER: {'type': ['string', 'null'], 'example': 'root'},
                cls.FIELD_UID: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_RUSER: {'type': ['string', 'null'], 'example': 'root'},
                cls.FIELD_RUID: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_COMM: {'type': ['string', 'null'], 'example': 'bash'},
                cls.FIELD_ARGS: {'type': ['string', 'null'], 'example': '/bin/bash --init-file /root'},
                cls.FIELD_CMD: {'type': ['string', 'null'], 'example': '/bin/bash --init-file /root'},
                cls.FIELD_PCPU: {'type': ['number', 'null'], 'example': 0.0},
                cls.FIELD_PMEM: {'type': ['number', 'null'], 'example': 0.1},
                cls.FIELD_CPUTIME: {'type': ['string', 'null'], 'example': '00:00:00'},
                cls.FIELD_ETIME: {'type': ['string', 'null'], 'example': '1-00:24:20'},
                cls.FIELD_TIME: {'type': ['string', 'null'], 'example': '00:00:00'},
                cls.FIELD_START: {'type': ['string', 'null'], 'example': 'Nov 08'},
                cls.FIELD_START_TIME: {'type': ['string', 'null'], 'example': 'lis08'},
                cls.FIELD_LSTART: {'type': ['string', 'null'], 'example': 'sob lis  8 21:06:55 2025'},
                cls.FIELD_STAT: {'type': ['string', 'null'], 'example': 'Ss+'},
                cls.FIELD_STATE: {'type': ['string', 'null'], 'example': 'S'},
                cls.FIELD_TTY: {'type': ['string', 'null'], 'example': 'pts/4'},
                cls.FIELD_PRI: {'type': ['integer', 'null'], 'example': 19},
                cls.FIELD_PRIORITY: {'type': ['integer', 'null'], 'example': 20},
                cls.FIELD_NICE: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_CLS: {'type': ['string', 'null'], 'example': 'TS'},
                cls.FIELD_POLICY: {'type': ['string', 'null'], 'example': 'TS'},
                cls.FIELD_RTPRIO: {'type': ['string', 'null'], 'example': '-'},
                cls.FIELD_VSZ: {'type': ['integer', 'null'], 'example': 11560},
                cls.FIELD_RSS: {'type': ['integer', 'null'], 'example': 5848},
                cls.FIELD_PSR: {'type': ['integer', 'null'], 'example': 3},
                cls.FIELD_CPU: {'type': ['string', 'null'], 'example': '-'},
                cls.FIELD_CGROUP: {'type': ['string', 'null'], 'example': '0::/user.slice/user-1000.sl'},
                cls.FIELD_NLWP: {'type': ['integer', 'null'], 'example': 1},
                cls.FIELD_THCOUNT: {'type': ['string', 'null'], 'example': '1'},
                cls.FIELD_WCHAN: {'type': ['string', 'null'], 'example': 'do_sel'},
                cls.FIELD_FLAGS: {'type': ['string', 'null'], 'example': '0'},
                cls.FIELD_F: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_MAJ_FLT: {'type': ['integer', 'null'], 'example': 0},
                cls.FIELD_MIN_FLT: {'type': ['integer', 'null'], 'example': 1542},
                cls.FIELD_SID: {'type': ['integer', 'null'], 'example': 471586},
                cls.FIELD_TGID: {'type': ['integer', 'null'], 'example': 471586},
                cls.FIELD_SESS: {'type': ['string', 'null'], 'example': '471586'}
            },
            'required': [],
            'additionalProperties': False
        }
    
    @classmethod
    def schema_public_list(cls) -> Dict[str, Any]:
        return {
            'type': 'array',
            'items': cls.schema_public()
        }