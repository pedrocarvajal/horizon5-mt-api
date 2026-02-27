import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from app.enums import SystemRole
from app.models.base import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=SystemRole.choices, default=SystemRole.PRODUCER)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "email"

    objects: "UserManager" = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
