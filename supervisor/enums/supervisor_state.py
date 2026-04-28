from enum import Enum


class SupervisorState(str, Enum):
    RUNNING = 'RUNNING'
    RESTARTING = 'RESTARTING'
    SHUTDOWN = 'SHUTDOWN'
    STOPPING = 'STOPPING'
    UNKNOWN = 'UNKNOWN'

