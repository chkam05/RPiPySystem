import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.test_auth_live import AuthLiveTests
from tests.test_users_live import UsersManagementLiveTests
from tests.test_supervisor_live import SupervisorLiveTests


if __name__ == '__main__':
    AuthLiveTests().run()
    UsersManagementLiveTests().run()
    SupervisorLiveTests().run()