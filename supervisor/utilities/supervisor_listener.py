from __future__ import annotations
from typing import Iterable, List, Optional
import os
import signal
import sys
import threading

from enums.supervisor_state import SupervisorState
from models.event_handler import EventHandler
from models.listener_config import ListenerConfig
from models.rule_result import RuleResult
from utilities.childutils_loader import load_childutils
from utilities.event_parser import EventParser
from utilities.logger import Logger


class SupervisorListener:
    def __init__(
        self,
        rules: Optional[Iterable[EventHandler]] = None,
        config: Optional[ListenerConfig] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        self.config = config or ListenerConfig()
        self.rules: List[EventHandler] = sorted(list(rules or []), key=lambda r: r.priority, reverse=True)
        self.logger = logger or Logger(self.config.service_name)
        self._stopping = False
        self._executed_once: set[str] = set()
        self._signal_once = threading.Event()

        if self.config.stop_on_signal:
            signal.signal(signal.SIGTERM, lambda signum, frame: self._handle_signal('SIGTERM'))
            signal.signal(signal.SIGINT, lambda signum, frame: self._handle_signal('SIGINT'))

    def _handle_signal(self, signal_name: str) -> None:
        if self._signal_once.is_set():
            return
        self._signal_once.set()
        self.logger.warning(f'{signal_name} received. Listener is stopping.')
        self._stopping = True

    def _format_event(self, event) -> str:
        target = event.process_name or event.group_name or 'supervisord'
        if event.group_name and event.process_name and event.group_name != event.process_name:
            target = f'{event.group_name}:{event.process_name}'
        pid = f' pid={event.pid}' if event.pid is not None else ''
        states = f' {event.from_state}->{event.to_state}' if event.from_state or event.to_state else ''
        return f'{event.event_name} [{target}{pid}]{states}'

    def _log_event(self, event) -> None:
        self.logger.info(self._format_event(event))
        if self.config.log_payload and event.raw_payload:
            payload = event.raw_payload[: self.config.max_payload_log_length]
            suffix = '...' if len(event.raw_payload) > self.config.max_payload_log_length else ''
            self.logger.debug(f'payload: {payload}{suffix}')

    def _matching_rules(self, event) -> List[EventHandler]:
        return [rule for rule in self.rules if rule.matches(event, self._executed_once)]

    def _execute_rule(self, rule: EventHandler, event) -> RuleResult:
        self.logger.debug(f'rule "{rule.name}" matched {event.event_name}')
        try:
            result = rule.action(event) or RuleResult.handled()
            if result.message:
                self.logger.info(f'rule "{rule.name}": {result.message}')
            if result.error:
                self.logger.error(f'rule "{rule.name}" error', result.error)
            if rule.run_once:
                self._executed_once.add(rule.name)
            return result
        except Exception as ex:
            self.logger.error(f'exception in rule "{rule.name}"', ex)
            return RuleResult.failed(f'exception in rule "{rule.name}"', ex)

    def dispatch(self, event) -> List[RuleResult]:
        matches = self._matching_rules(event)
        if not matches:
            return []

        results: List[RuleResult] = []
        for rule in matches:
            results.append(self._execute_rule(rule, event))
            if not self.config.execute_all_matching_rules:
                break
        return results

    def handle(self, headers, payload) -> None:
        event = EventParser.parse(headers, payload)
        self._log_event(event)
        self.dispatch(event)

        if (
            self.config.stop_on_supervisor_stopping
            and event.is_supervisor_event
            and event.supervisor_state == SupervisorState.STOPPING
        ):
            self._stopping = True

    def run(self) -> int:
        childutils = load_childutils()
        self.logger.info('Supervisor listener started. Waiting for events.')
        while not self._stopping:
            try:
                headers, payload = childutils.listener.wait()
                self.handle(headers, payload)
            except Exception as ex:
                self.logger.error('unexpected listener exception', ex)
            finally:
                if not self._stopping:
                    childutils.listener.ok()
        return 0

    def stop_process(self) -> None:
        self._stopping = True

    def force_exit(self, code: int = 0) -> None:
        os._exit(code)
