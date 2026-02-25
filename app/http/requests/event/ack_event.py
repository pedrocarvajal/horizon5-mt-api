import json

from rest_framework import serializers

from app.http.requests.event.push_event import MAX_PAYLOAD_SIZE, _check_nesting_depth
from app.http.requests.fields import ObjectIdField


class AckEventRequestSerializer(serializers.Serializer):
    event_id = ObjectIdField()
    response = serializers.DictField(required=False, allow_null=True)

    def validate_response(self, value):
        if value is None:
            return value
        serialized = json.dumps(value)
        if len(serialized.encode()) > MAX_PAYLOAD_SIZE:
            raise serializers.ValidationError(f"Response size exceeds maximum of {MAX_PAYLOAD_SIZE} bytes.")
        _check_nesting_depth(value)
        return value
