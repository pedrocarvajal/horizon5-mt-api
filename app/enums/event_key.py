from enum import Enum

from rest_framework import serializers


class EventKey(Enum):
    POST_ORDER = "post.order"
    GET_ORDER = "get.order"
    PUT_ORDER = "put.order"
    DELETE_ORDER = "delete.order"
    GET_ACCOUNT_INFO = "get.account.info"
    GET_KLINES = "get.klines"
    GET_TICKER = "get.ticker"
    PATCH_ACCOUNT_DISABLE = "patch.account.disable"
    PATCH_ACCOUNT_ENABLE = "patch.account.enable"

    def schema(self) -> dict:
        schemas = {
            EventKey.POST_ORDER: {
                "symbol": {"type": "string", "required": True},
                "strategy": {"type": "integer", "required": True},
                "type": {"type": "string", "required": True, "choices": ["buy", "sell"]},
                "volume": {"type": "float", "required": True, "min_value": 0.01},
                "price": {"type": "float", "required": False},
                "stop_loss": {"type": "float", "required": False},
                "take_profit": {"type": "float", "required": False},
                "comment": {"type": "string", "required": False, "max_length": 255},
            },
            EventKey.GET_ORDER: {
                "id": {"type": "integer", "required": True},
            },
            EventKey.PUT_ORDER: {
                "id": {"type": "integer", "required": True},
                "stop_loss": {"type": "float", "required": False},
                "take_profit": {"type": "float", "required": False},
            },
            EventKey.DELETE_ORDER: {
                "id": {"type": "integer", "required": True},
            },
            EventKey.GET_ACCOUNT_INFO: {},
            EventKey.GET_KLINES: {},
            EventKey.GET_TICKER: {},
            EventKey.PATCH_ACCOUNT_DISABLE: {},
            EventKey.PATCH_ACCOUNT_ENABLE: {},
        }
        return schemas[self]

    def serializer(self) -> type[serializers.Serializer]:
        fields = {}
        schema = self.schema()

        if not schema:
            return _build_empty_serializer(self.value)

        field_type_map = {
            "string": serializers.CharField,
            "float": serializers.FloatField,
            "integer": serializers.IntegerField,
        }

        for field_name, definition in schema.items():
            field_class = field_type_map[definition["type"]]
            kwargs = {"required": definition.get("required", False)}

            if not kwargs["required"]:
                kwargs["default"] = definition.get("default", None)
                if kwargs["default"] is None:
                    kwargs["allow_null"] = True

            if "choices" in definition:
                field_class = serializers.ChoiceField
                kwargs["choices"] = [(choice, choice) for choice in definition["choices"]]

            if "min_value" in definition:
                kwargs["min_value"] = definition["min_value"]

            if "max_value" in definition:
                kwargs["max_value"] = definition["max_value"]

            if "max_length" in definition:
                kwargs["max_length"] = definition["max_length"]

            fields[field_name] = field_class(**kwargs)

        return type(f"{self.value}PayloadSerializer", (serializers.Serializer,), fields)


def _build_empty_serializer(name: str) -> type[serializers.Serializer]:
    def validate(_self, attrs):
        if attrs:
            raise serializers.ValidationError("This event key does not accept any payload fields.")

        return attrs

    return type(f"{name}PayloadSerializer", (serializers.Serializer,), {"validate": validate})
