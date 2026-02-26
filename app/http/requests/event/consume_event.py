from rest_framework import serializers

from app.enums import EventKey

VALID_EVENT_KEYS = {k.value for k in EventKey}


class ConsumeEventRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=50, min_value=1, max_value=100)
    key = serializers.CharField(required=False)

    def validate_key(self, value: str) -> list[str]:
        keys = [k.strip() for k in value.split(",") if k.strip()]
        invalid = [k for k in keys if k not in VALID_EVENT_KEYS]

        if invalid:
            raise serializers.ValidationError(
                f"Invalid event key(s): {', '.join(invalid)} - valid keys: {', '.join(sorted(VALID_EVENT_KEYS))}"
            )

        return keys
