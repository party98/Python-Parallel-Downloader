import enum


class DownloadStatus(enum.Enum):
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    FINISHED = 4
    ERROR_OCCURED = 5
    INITIALIZING = 6
    STARTED = 7
    READY = 8
