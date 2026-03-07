def extract_message(detail, fallback: str) -> str:
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail and isinstance(detail[0], str):
        return detail[0]
    return fallback


def extract_validation_message(detail, fallback: str, field: str = "") -> str:
    if isinstance(detail, str):
        return f"{field}: {detail}" if field else detail
    if isinstance(detail, list) and detail:
        return extract_validation_message(detail[0], fallback, field)
    if isinstance(detail, dict):
        first_key = next(iter(detail), None)
        if first_key is not None:
            label = "" if first_key == "non_field_errors" else first_key
            return extract_validation_message(detail[first_key], fallback, label)
    return fallback
