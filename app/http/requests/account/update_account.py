from rest_framework import serializers

from app.enums import AccountStatus


class UpdateAccountRequestSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=AccountStatus.choices, required=False)
    broker = serializers.CharField(max_length=255, required=False, allow_blank=True)
    server = serializers.CharField(max_length=255, required=False, allow_blank=True)
    currency = serializers.CharField(max_length=10, required=False, allow_blank=True)
    leverage = serializers.IntegerField(required=False, min_value=1)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    equity = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    margin = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    free_margin = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    profit = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    margin_level = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate(self, data: dict) -> dict:
        if not data:
            raise serializers.ValidationError("At least one field must be provided.")
        return data
