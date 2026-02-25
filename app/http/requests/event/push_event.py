import json
import re

from rest_framework import serializers

EVENT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*$")
MAX_PAYLOAD_SIZE = 65536
MAX_NESTING_DEPTH = 5


def _check_nesting_depth(data, current_depth=0):
    if current_depth > MAX_NESTING_DEPTH:
        raise serializers.ValidationError(f"Payload nesting depth exceeds maximum of {MAX_NESTING_DEPTH} levels.")
    if isinstance(data, dict):
        for value in data.values():
            _check_nesting_depth(value, current_depth + 1)
    elif isinstance(data, list):
        for item in data:
            _check_nesting_depth(item, current_depth + 1)


class PushEventRequestSerializer(serializers.Serializer):
    key = serializers.CharField(min_length=1, max_length=255)
    payload = serializers.DictField()

    def validate_key(self, value):
        if not EVENT_KEY_PATTERN.match(value):
            raise serializers.ValidationError(
                "Key must match pattern: lowercase letters/numbers separated by dots (e.g. 'order.created')."
            )
        return value

    def validate_payload(self, value):
        serialized = json.dumps(value)
        if len(serialized.encode()) > MAX_PAYLOAD_SIZE:
            raise serializers.ValidationError(f"Payload size exceeds maximum of {MAX_PAYLOAD_SIZE} bytes.")
        _check_nesting_depth(value)
        return value
