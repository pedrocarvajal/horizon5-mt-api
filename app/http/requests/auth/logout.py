from rest_framework import serializers


class LogoutRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField(min_length=1)
