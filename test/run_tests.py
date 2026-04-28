from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Type

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test.auth_test import AuthTest
from test.core import TestCase
from test.supervisor_test import SupervisorTest
from test.users_test import UsersTest


@dataclass(frozen=True)
class TestSuiteEntry:
    name: str
    test_class: Type[TestCase]


TEST_SUITES: list[TestSuiteEntry] = [
    TestSuiteEntry('auth_test', AuthTest),
    TestSuiteEntry('users_test', UsersTest),
    TestSuiteEntry('supervisor_test', SupervisorTest),
]


def run_all() -> bool:
    print('[run_tests.py] starting grouped tests')

    passed_count = 0
    for index, entry in enumerate(TEST_SUITES, start=1):
        print(f'[run_tests.py] {index}/{len(TEST_SUITES)} {entry.name}: start')
        passed = entry.test_class().run(entry.name)
        print(f'[run_tests.py] {entry.name}: {passed}')
        if passed:
            passed_count += 1

    print(f'[run_tests.py] summary: {passed_count}/{len(TEST_SUITES)} suites passed')
    return passed_count == len(TEST_SUITES)


if __name__ == '__main__':
    ok = run_all()
    raise SystemExit(0 if ok else 1)
