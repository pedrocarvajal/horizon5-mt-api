import base64
import binascii
import json
from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from rest_framework import serializers


class HistoryEventRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(default=50, min_value=1, max_value=100)
    cursor = serializers.CharField(required=False, max_length=2048)

    def validate_cursor(self, value):
        try:
            decoded = json.loads(base64.b64decode(value))
        except (json.JSONDecodeError, binascii.Error, UnicodeDecodeError) as exc:
            raise serializers.ValidationError("Invalid cursor format.") from exc

        if not isinstance(decoded, dict) or "created_at" not in decoded or "_id" not in decoded:
            raise serializers.ValidationError("Cursor must contain 'created_at' and '_id'.")

        try:
            decoded["created_at"] = datetime.fromisoformat(decoded["created_at"])
        except (ValueError, TypeError) as exc:
            raise serializers.ValidationError("Invalid 'created_at' in cursor.") from exc

        try:
            decoded["_id"] = ObjectId(decoded["_id"])
        except (InvalidId, TypeError) as exc:
            raise serializers.ValidationError("Invalid '_id' in cursor.") from exc

        return decoded
