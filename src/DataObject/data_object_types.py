from enum import Enum

class OperationType(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
