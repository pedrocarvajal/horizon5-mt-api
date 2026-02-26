from rest_framework import serializers


class CreateStrategySnapshotRequestSerializer(serializers.Serializer):
    account_id = serializers.IntegerField()
    strategy_id = serializers.UUIDField()
    nav = serializers.DecimalField(max_digits=15, decimal_places=2)
    drawdown_pct = serializers.DecimalField(max_digits=8, decimal_places=4)
    daily_pnl = serializers.DecimalField(max_digits=15, decimal_places=2)
    floating_pnl = serializers.DecimalField(max_digits=15, decimal_places=2)
    open_order_count = serializers.IntegerField(min_value=0)
    exposure_lots = serializers.DecimalField(max_digits=10, decimal_places=4)
