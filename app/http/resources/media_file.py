from rest_framework import serializers


class MediaFileResource(serializers.Serializer):
    id = serializers.UUIDField()
    account_id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    file_name = serializers.CharField()
    original_name = serializers.CharField()
    content_type = serializers.CharField()
    size = serializers.IntegerField()
    expires_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
