from rest_framework import serializers


class ConsumeEventRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=50, min_value=1, max_value=100)
