from core.data.enum_str import StrEnum


class SupervisorMethod(StrEnum):
    GET_ALL_PROCESS_INFO = 'getAllProcessInfo'
    GET_PROCESS_INFO = 'getProcessInfo'
    START_PROCESS = 'startProcess'
    STOP_PROCESS = 'stopProcess'
    GET_ALL_CONFIG_INFO = 'getAllConfigInfo'
