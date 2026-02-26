from rest_framework import serializers

from app.enums import EventKey, EventStatus


class HistoryEventRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=50, min_value=1, max_value=100)
    status = serializers.ChoiceField(
        choices=[(s.value, s.name) for s in EventStatus],
        required=False,
    )
    key = serializers.ChoiceField(
        choices=[(k.value, k.name) for k in EventKey],
        required=False,
    )
