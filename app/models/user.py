import uuid

from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from app.enums import SystemRole
from app.models.base import BaseModel


class User(AbstractBaseUser, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=SystemRole.choices, default=SystemRole.PRODUCER)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
