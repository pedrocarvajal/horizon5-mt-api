import uuid
from decimal import Decimal

from django.db import models

from app.models.base import BaseModel


class Account(BaseModel):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="accounts")
    user_id: uuid.UUID
    broker = models.CharField(max_length=255, null=True, blank=True)
    server = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    leverage = models.IntegerField(null=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    equity = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    margin = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    free_margin = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    margin_level = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    class Meta:
        db_table = "accounts"

    def __str__(self):
        return str(self.id)
