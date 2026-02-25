import uuid

from django.db import models

from app.models.base import BaseModel


class Account(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="accounts")
    account_number = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return self.account_number
