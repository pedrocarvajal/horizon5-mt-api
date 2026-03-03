def extract_message(detail, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail and isinstance(detail[0], str):
        return detail[0]
    return fallback


def extract_validation_message(detail, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return extract_validation_message(detail[0], fallback)
    if isinstance(detail, dict):
        first_value = next(iter(detail.values()), None)
        if first_value is not None:
            return extract_validation_message(first_value, fallback)
    return fallback
