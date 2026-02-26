import json

from rest_framework import serializers

MAX_PAYLOAD_SIZE = 65536
MAX_NESTING_DEPTH = 5


def check_nesting_depth(data, current_depth=0):
    if current_depth > MAX_NESTING_DEPTH:
        raise serializers.ValidationError(f"Payload nesting depth exceeds maximum of {MAX_NESTING_DEPTH} levels.")

    if isinstance(data, dict):
        for value in data.values():
            check_nesting_depth(value, current_depth + 1)

    elif isinstance(data, list):
        for item in data:
            check_nesting_depth(item, current_depth + 1)


def validate_dict_payload(value):
    serialized = json.dumps(value)

    if len(serialized.encode()) > MAX_PAYLOAD_SIZE:
        raise serializers.ValidationError(f"Payload size exceeds maximum of {MAX_PAYLOAD_SIZE} bytes.")

    check_nesting_depth(value)
    return value
