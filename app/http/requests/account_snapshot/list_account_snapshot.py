from rest_framework import serializers

from app.http.requests.list_request import ListRequestSerializer


class ListAccountSnapshotRequestSerializer(ListRequestSerializer):
    account_id = serializers.IntegerField()
