from rest_framework import serializers


class EventResource(serializers.Serializer):
    id = serializers.SerializerMethodField()
    consumer_id = serializers.CharField(allow_null=True)
    account_id = serializers.CharField()
    user_id = serializers.CharField()
    key = serializers.CharField()
    payload = serializers.DictField()
    response = serializers.DictField(allow_null=True)
    status = serializers.CharField()
    delivered_at = serializers.DateTimeField(allow_null=True)
    processed_at = serializers.DateTimeField(allow_null=True)
    attempts = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_id(self, obj):
        return str(obj["_id"])
