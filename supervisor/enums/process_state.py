from enum import Enum


class ProcessState(str, Enum):
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    BACKOFF = 'BACKOFF'
    STOPPING = 'STOPPING'
    EXITED = 'EXITED'
    STOPPED = 'STOPPED'
    FATAL = 'FATAL'
    UNKNOWN = 'UNKNOWN'

