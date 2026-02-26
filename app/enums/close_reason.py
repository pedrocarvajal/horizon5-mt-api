from enum import StrEnum


class CloseReason(StrEnum):
    TP = "tp"
    SL = "sl"
    EXPERT = "expert"
    CLIENT = "client"
    MOBILE = "mobile"
    WEB = "web"
    UNKNOWN = "unknown"
