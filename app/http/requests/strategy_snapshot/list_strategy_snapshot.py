from rest_framework import serializers


class ListStrategySnapshotRequestSerializer(serializers.Serializer):
    strategy_id = serializers.UUIDField()
    account_id = serializers.IntegerField(required=False)
    page = serializers.IntegerField(default=1, min_value=1)
    per_page = serializers.IntegerField(default=50, min_value=1, max_value=100)
