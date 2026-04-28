from core.data.enum_str import StrEnum


class SupervisorProcessState(StrEnum):
    STOPPED = 'STOPPED'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    BACKOFF = 'BACKOFF'
    STOPPING = 'STOPPING'
    EXITED = 'EXITED'
    FATAL = 'FATAL'
    UNKNOWN = 'UNKNOWN'

    @classmethod
    def start_success_states(cls) -> set[str]:
        return {cls.STARTING.value, cls.RUNNING.value}

    @classmethod
    def stop_success_states(cls) -> set[str]:
        return {
            cls.STOPPED.value,
            cls.EXITED.value,
            cls.FATAL.value,
            cls.STOPPING.value,
        }
