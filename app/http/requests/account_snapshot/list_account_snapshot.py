from rest_framework import serializers


class ListAccountSnapshotRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    page = serializers.IntegerField(default=1, min_value=1)
    per_page = serializers.IntegerField(default=50, min_value=1, max_value=100)
