from core.data.enum_str import StrEnum


class SupervisorAction(StrEnum):
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'
    STOP_ALL = 'stop_all'
