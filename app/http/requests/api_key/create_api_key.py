from django.utils import timezone
from rest_framework import serializers


class CreateApiKeyRequestSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=1, max_length=100)
    allowed_ips = serializers.ListField(
        child=serializers.IPAddressField(),
        required=False,
        default=list,
        max_length=20,
    )
    expires_at = serializers.DateTimeField(required=False, default=None)

    def validate_expires_at(self, value):
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")

        return value
