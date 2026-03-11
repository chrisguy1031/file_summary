from enum import IntEnum, Enum

class FileStatus(IntEnum):
    """File status enumeration."""
    UPLOADED = 1
    DONE = 2
    FAILED = 3