from django.utils import timezone
from rest_framework import serializers


class UpdateApiKeyRequestSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=1, max_length=100, required=False)
    allowed_ips = serializers.ListField(
        child=serializers.IPAddressField(),
        required=False,
        max_length=20,
    )
    is_active = serializers.BooleanField(required=False)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_expires_at(self, value):
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Expiration date must be in the future.")

        return value
