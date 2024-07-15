from enum import Enum


class RecordStatus(int, Enum):
    FOUND = 0
    NOT_FOUND = 1
    CREATED = 2
    NOT_CREATED = 3
    DELETED = 4
    NOT_DELETED = 5
    ERROR = 6
