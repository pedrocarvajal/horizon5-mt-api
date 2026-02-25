from rest_framework import serializers

from app.http.requests.fields import ObjectIdField


class EventResponseRequestSerializer(serializers.Serializer):
    event_id = ObjectIdField()
