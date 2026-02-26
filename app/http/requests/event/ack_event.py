from rest_framework import serializers

from app.http.requests.fields import ObjectIdField
from app.http.requests.validators import validate_dict_payload


class AckEventRequestSerializer(serializers.Serializer):
    event_id = ObjectIdField()
    response = serializers.DictField(required=False, allow_null=True)

    def validate_response(self, value):
        if value is None:
            return value

        return validate_dict_payload(value)
