from enum import Enum


class RuleDecision(str, Enum):
    HANDLED = 'HANDLED'
    IGNORED = 'IGNORED'
    FAILED = 'FAILED'

