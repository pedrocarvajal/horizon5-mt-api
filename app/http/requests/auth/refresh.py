from rest_framework import serializers


class RefreshRequestSerializer(serializers.Serializer):
    refresh = serializers.CharField()
