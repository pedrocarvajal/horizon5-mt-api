from rest_framework import serializers


class UpsertStrategyRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    id = serializers.UUIDField()
    symbol = serializers.CharField(max_length=50)
    prefix = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    magic_number = serializers.IntegerField()
    balance = serializers.DecimalField(max_digits=15, decimal_places=2)
