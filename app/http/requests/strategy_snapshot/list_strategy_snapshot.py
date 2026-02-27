from rest_framework import serializers

from app.http.requests.list_request import ListRequestSerializer


class ListStrategySnapshotRequestSerializer(ListRequestSerializer):
    strategy_id = serializers.UUIDField()
    account_id = serializers.IntegerField(required=False)
