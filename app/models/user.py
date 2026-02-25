import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from app.enums import SystemRole
from app.models.base import BaseModel, SoftDeleteManager, SoftDeleteMixin


class UserManager(SoftDeleteManager, BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", SystemRole.ROOT)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, SoftDeleteMixin, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=SystemRole.choices, default=SystemRole.PRODUCER)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list] = []

    class Meta:
        db_table = "users"

    @property
    def is_staff(self):
        return self.role == SystemRole.ROOT

    def has_perm(self, _perm, _obj=None):
        return self.role == SystemRole.ROOT

    def has_module_perms(self, _app_label):
        return self.role == SystemRole.ROOT

    def __str__(self):
        return self.email
