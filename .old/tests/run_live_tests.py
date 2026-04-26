import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.test_auth_sessions import TestAuthSessions
from tests.test_auth_users import TestAuthUsers
from tests.test_system_supervisor import TestSystemSupervisor


if __name__ == '__main__':
    TestAuthSessions().run()
    TestAuthUsers().run()
    TestSystemSupervisor().run()