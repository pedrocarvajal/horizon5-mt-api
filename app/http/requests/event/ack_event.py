import json

from rest_framework import serializers

from app.http.requests.event.push_event import MAX_PAYLOAD_SIZE, _check_nesting_depth


class AckEventRequestSerializer(serializers.Serializer):
    response = serializers.DictField(required=False, allow_null=True)

    def validate_response(self, value):
        if value is None:
            return value
        serialized = json.dumps(value)
        if len(serialized.encode()) > MAX_PAYLOAD_SIZE:
            raise serializers.ValidationError(f"Response size exceeds maximum of {MAX_PAYLOAD_SIZE} bytes.")
        _check_nesting_depth(value)
        return value
