from rest_framework import serializers


class CreateLogRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    strategy_id = serializers.UUIDField(required=False, allow_null=True)
    level = serializers.CharField(max_length=20)
    message = serializers.CharField(max_length=5000)
