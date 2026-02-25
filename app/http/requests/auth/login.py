from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5, max_length=254)
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
