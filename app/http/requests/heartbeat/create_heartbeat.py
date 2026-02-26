from rest_framework import serializers

from app.enums import HeartbeatEvent, HeartbeatSystem


class CreateHeartbeatRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    strategy_id = serializers.UUIDField(required=False, allow_null=True)
    event = serializers.ChoiceField(choices=[(e.value, e.value) for e in HeartbeatEvent])
    system = serializers.ChoiceField(choices=[(s.value, s.value) for s in HeartbeatSystem])
