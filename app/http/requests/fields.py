from bson import ObjectId
from bson.errors import InvalidId
from django.core.validators import RegexValidator
from rest_framework import serializers


class ObjectIdField(serializers.CharField):
    def __init__(self, **kwargs):
        kwargs.setdefault("min_length", 24)
        kwargs.setdefault("max_length", 24)
        super().__init__(**kwargs)
        self.validators.append(
            RegexValidator(
                regex=r"^[a-f0-9]{24}$",
                message="Must be a 24-character hex string.",
            )
        )

    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        try:
            return ObjectId(value)

        except (InvalidId, TypeError) as error:
            raise serializers.ValidationError("Invalid ObjectId format.") from error
