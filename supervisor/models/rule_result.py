from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from enums.rule_decision import RuleDecision


@dataclass(frozen=True)
class RuleResult:
    decision: RuleDecision
    message: str = ''
    error: Optional[Exception] = None

    @classmethod
    def handled(cls, message: str = '') -> RuleResult:
        return cls(RuleDecision.HANDLED, message)

    @classmethod
    def ignored(cls, message: str = '') -> RuleResult:
        return cls(RuleDecision.IGNORED, message)

    @classmethod
    def failed(cls, message: str, error: Optional[Exception] = None) -> RuleResult:
        return cls(RuleDecision.FAILED, message, error)

