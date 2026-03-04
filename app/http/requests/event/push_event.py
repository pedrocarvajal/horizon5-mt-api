from rest_framework import serializers

from app.enums import EventKey
from app.http.requests.validators import validate_dict_payload
from app.models import Account, Strategy


class PushEventRequestSerializer(serializers.Serializer):
    key = serializers.ChoiceField(choices=[(event_key.value, event_key.name) for event_key in EventKey])
    payload = serializers.DictField()

    def validate_payload(self, value):
        return validate_dict_payload(value)

    def validate(self, attrs):
        account_id = self.context["account_id"]

        if not Account.objects.filter(id=account_id).exists():
            raise serializers.ValidationError({"detail": "Account not found."})

        event_key = EventKey(attrs["key"])
        serializer_class = event_key.serializer()
        serializer = serializer_class(data=attrs["payload"])
        serializer.is_valid(raise_exception=True)
        attrs["payload"] = {k: v for k, v in serializer.validated_data.items() if v is not None}

        magic_number = attrs["payload"].get("strategy")
        if (
            magic_number is not None
            and not Strategy.objects.filter(account_id=account_id, magic_number=magic_number).exists()
        ):
            raise serializers.ValidationError(
                {"payload": {"strategy": f"Strategy with magic number {magic_number} not found for this account."}}
            )

        return attrs
