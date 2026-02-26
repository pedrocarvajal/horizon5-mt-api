from rest_framework import serializers


class CreateAccountSnapshotRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    equity = serializers.DecimalField(max_digits=15, decimal_places=2)
    profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    margin_level = serializers.DecimalField(max_digits=10, decimal_places=2)
    open_positions = serializers.IntegerField(min_value=0)
    drawdown_pct = serializers.DecimalField(max_digits=8, decimal_places=4)
    daily_pnl = serializers.DecimalField(max_digits=15, decimal_places=2)
    floating_pnl = serializers.DecimalField(max_digits=15, decimal_places=2)
    open_order_count = serializers.IntegerField(min_value=0)
    exposure_lots = serializers.DecimalField(max_digits=10, decimal_places=4)
