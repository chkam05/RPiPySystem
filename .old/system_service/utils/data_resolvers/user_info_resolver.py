import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from system_service.models.system.users.os_user_info import OSUserInfo
from system_service.models.system.users.os_user_logged_in import OSUserLoggedIn


class UserInfoResolver:
    """Static utility for collecting user accounts and logged-in sessions."""

    def __new__(cls, *args, **kwargs):
        """Prevent instantiation of this static utility class."""
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    
    # --------------------------------------------------------------------------
    # --- INTERNAL HELPERS ---
    # --------------------------------------------------------------------------

    @classmethod
    def _run(cls, cmd: List[str]) -> List[str]:
        """Run command and return non-empty lines."""
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)
        return [ln.rstrip('\n') for ln in out.splitlines() if ln.strip() != '']

    @classmethod
    def _can_login(cls, uid: int, shell: str) -> bool:
        """Compute can_login using UID and login shell."""
        shell_invalid = shell.endswith('nologin') or shell.endswith('false')
        return (uid >= 1000 or uid == 0) and not shell_invalid

    @classmethod
    def _parse_who_u(cls, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse 'who -u' lines into dicts."""
        # Example lines:
        # chkam    sshd         2025-11-11 19:39   ?         11856 (192.168.1.100)
        # chkam    sshd pts/1   2025-11-11 18:01 05:43        2690 (192.168.1.100)
        out: List[Dict[str, Any]] = []
        for ln in lines:
            comment = None
            m_comment = re.search(r'\(([^)]+)\)\s*$', ln)
            if m_comment:
                comment = m_comment.group(1)
                ln = ln[:m_comment.start()].rstrip()

            parts = ln.split()
            if len(parts) < 6:
                continue

            login = parts[0]

            # Find date token index.
            idx_date = None
            for i in range(1, min(6, len(parts))):
                if re.match(r'\d{4}-\d{2}-\d{2}$', parts[i]):
                    idx_date = i
                    break
            if idx_date is None or idx_date + 3 > len(parts):
                continue

            term_tokens = parts[1:idx_date] # Could be ['sshd'] or ['sshd','pts/1'] or ['tty1'].
            term = ' '.join(term_tokens) if term_tokens else None
            date = parts[idx_date]
            clock = parts[idx_date + 1]
            idle_or_time = parts[idx_date + 2]
            pid_str = parts[idx_date + 3]
            try:
                pid = int(pid_str)
            except ValueError:
                pid = None

            out.append({
                'login': login,
                'term': term,
                'time': f'{date} {clock}',
                'idle_or_time': idle_or_time,
                'pid': pid,
                'comment': comment
            })
        return out

    @classmethod
    def _parse_w_h(cls, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse 'w -h' lines into dicts."""
        # Example lines:
        # chkam             192.168.1.100    19:39           0.00s  0.09s sshd-session: chkam [priv]
        # chkam    pts/0    192.168.1.100    17:51    5:53m  0.08s  0.08s -bash
        out: List[Dict[str, Any]] = []
        for ln in lines:
            parts = ln.split()
            if len(parts) < 6:
                continue

            login = parts[0]
            idx = 1
            tty = None
            if idx < len(parts) and ('/' in parts[idx] or parts[idx].startswith('tty') or parts[idx].startswith('pts')):
                tty = parts[idx]
                idx += 1

            if idx >= len(parts):
                continue
            host = parts[idx]; idx += 1

            if idx >= len(parts):
                continue
            login_at = parts[idx]; idx += 1

            if idx >= len(parts):
                continue
            idle = parts[idx]; idx += 1

            if idx + 1 >= len(parts):
                continue
            jcpu = parts[idx]; pcpu = parts[idx + 1]; idx += 2

            what = ' '.join(parts[idx:]) if idx < len(parts) else None

            out.append({
                'login': login,
                'tty': tty,
                'from': host,
                'login_at': login_at,
                'idle': idle,
                'jcpu': jcpu,
                'pcpu': pcpu,
                'what': what
            })
        return out
    
    # --------------------------------------------------------------------------
    # --- PUBLIC METHODS ---
    # --------------------------------------------------------------------------

    @classmethod
    def get_system_users(
        cls,
        loggable_users_only: bool = False,
        fname: Optional[str] = None
    ) -> List[OSUserInfo]:
        """Return system users from getent; optional filter by can_login and name substring."""
        rows = cls._run(['getent', 'passwd'])
        users: List[OSUserInfo] = []

        for ln in rows:
            # login:passwd:UID:GID:gecos:home:shell.
            parts = ln.split(':')
            if len(parts) < 7:
                continue

            login, _passwd, uid, gid, gecos, home, shell = parts[:7]
            try:
                uid_i = int(uid)
                gid_i = int(gid)
            except ValueError:
                continue

            can_login = cls._can_login(uid_i, shell)

            if loggable_users_only and not can_login:
                continue

            if fname and fname.strip():
                if fname.lower() not in login.lower():
                    continue

            users.append(OSUserInfo(
                user_name=login,
                user_id=uid_i,
                group_id=gid_i,
                user_info=gecos,
                home_directory=home,
                shell_path=shell,
                can_login=can_login
            ))

        return users

    @classmethod
    def get_logged_in_users(cls) -> List[OSUserLoggedIn]:
        """Return logged-in users merged from who -u and w -h."""
        who_rows = cls._parse_who_u(cls._run(['who', '-u']))
        w_rows = cls._parse_w_h(cls._run(['w', '-h']))

        # Index w-rows by (login, tty) where possible.
        idx_w: Dict[Tuple[str, Optional[str]], Dict[str, Any]] = {}
        for r in w_rows:
            key = (r.get('login'), r.get('tty'))
            idx_w[key] = r

        sessions: List[OSUserLoggedIn] = []
        for wr in who_rows:
            key = (wr.get('login'), wr.get('term'))
            wr_w = idx_w.get(key)
            if wr_w is None:
                # Fallback by login only.
                wr_w = next((x for x in w_rows if x.get('login') == wr.get('login')), None)

            # Build dict for model.
            payload: Dict[str, Any] = {
                OSUserLoggedIn.FIELD_USER_NAME: wr.get('login'),
                OSUserLoggedIn.FIELD_TERMINAL_NAME: wr.get('term'),
                OSUserLoggedIn.FIELD_LOGGED_AT: wr.get('time'),
                OSUserLoggedIn.FIELD_REMOTE_HOST: wr_w.get('from') if wr_w else None,
                OSUserLoggedIn.FIELD_IDLE_TIME: wr.get('idle_or_time'),
                OSUserLoggedIn.FIELD_JOB_CPU_TIME: wr_w.get('jcpu') if wr_w else None,
                OSUserLoggedIn.FIELD_PROCESS_CPU_TIME: wr_w.get('pcpu') if wr_w else None,
                OSUserLoggedIn.FIELD_SESSION_COMMAND: wr_w.get('what') if wr_w else None,
                OSUserLoggedIn.FIELD_PROCESS_ID: wr.get('pid'),
                OSUserLoggedIn.FIELD_SESSION_COMMENT: wr.get('comment'),
            }
            sessions.append(OSUserLoggedIn.from_dict(payload))

        return sessions