from enum import StrEnum


class HeartbeatEvent(StrEnum):
    ON_INIT = "on_init"
    ON_RUNNING = "on_running"
    ON_DEINIT = "on_deinit"
    ON_ERROR = "on_error"
