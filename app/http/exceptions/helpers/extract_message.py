def extract_message(detail, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail and isinstance(detail[0], str):
        return detail[0]
    return fallback
