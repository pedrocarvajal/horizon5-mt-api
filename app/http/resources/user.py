from typing import ClassVar

from rest_framework import serializers

from app.models import User


class UserResource(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: ClassVar[list] = ["id", "email", "role", "is_active", "created_at"]
        read_only_fields = fields
