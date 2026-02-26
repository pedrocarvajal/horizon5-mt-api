import hashlib
import secrets
import uuid
from typing import ClassVar

from django.db import models
from django.utils import timezone

from app.models.base import BaseModel


class ApiKey(BaseModel):
    PREFIX_LENGTH = 8
    KEY_LENGTH = 48

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100)
    key_hash = models.CharField(max_length=64, unique=True, db_index=True)
    prefix = models.CharField(max_length=8)
    allowed_ips = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "api_keys"
        ordering: ClassVar[list] = ["-created_at"]

    def __str__(self):
        return f"{self.prefix}... ({self.name})"

    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        raw_key = secrets.token_hex(cls.KEY_LENGTH)
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return raw_key, key_hash

    @classmethod
    def hash_key(cls, raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def is_ip_allowed(self, ip: str) -> bool:
        if not self.allowed_ips:
            return True

        return ip in self.allowed_ips

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False

        return self.expires_at <= timezone.now()

    @property
    def is_usable(self) -> bool:
        return self.is_active and not self.is_expired
