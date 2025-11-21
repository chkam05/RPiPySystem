from utils.models.base_str_enum import BaseStrEnum


class ServiceAction(BaseStrEnum):
    START = 'start'
    STOP = 'stop'
    RESTART = 'restart'