from rest_framework import serializers

from app.enums import CloseReason, OrderStatus


class UpsertOrderRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    account_id = serializers.IntegerField()
    strategy_id = serializers.UUIDField(required=False, allow_null=True)
    deal_id = serializers.IntegerField(required=False, allow_null=True)
    position_id = serializers.IntegerField(required=False, allow_null=True)
    source = serializers.CharField(max_length=50, required=False, allow_blank=True)
    symbol = serializers.CharField(max_length=50)
    side = serializers.CharField(max_length=10)
    status = serializers.ChoiceField(choices=[(s.value, s.value) for s in OrderStatus])
    is_market_order = serializers.BooleanField(default=False)
    volume = serializers.DecimalField(max_digits=10, decimal_places=4)
    signal_price = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)
    open_at_price = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)
    open_price = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)
    close_price = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)
    take_profit = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)
    stop_loss = serializers.DecimalField(max_digits=15, decimal_places=5, required=False)
    profit = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    gross_profit = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    commission = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    swap = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    close_reason = serializers.ChoiceField(
        choices=[(r.value, r.value) for r in CloseReason],
        required=False,
        allow_blank=True,
    )
    signal_at = serializers.DateTimeField(required=False, allow_null=True)
    opened_at = serializers.DateTimeField(required=False, allow_null=True)
    closed_at = serializers.DateTimeField(required=False, allow_null=True)
