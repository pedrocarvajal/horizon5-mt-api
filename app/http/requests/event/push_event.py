from rest_framework import serializers

from app.enums import EventKey
from app.http.requests.validators import validate_dict_payload


class PushEventRequestSerializer(serializers.Serializer):
    key = serializers.ChoiceField(choices=[(event_key.value, event_key.name) for event_key in EventKey])
    payload = serializers.DictField()

    def validate_payload(self, value):
        return validate_dict_payload(value)

    def validate(self, attrs):
        event_key = EventKey(attrs["key"])
        serializer_class = event_key.serializer()
        serializer = serializer_class(data=attrs["payload"])
        serializer.is_valid(raise_exception=True)
        attrs["payload"] = serializer.validated_data

        return attrs
