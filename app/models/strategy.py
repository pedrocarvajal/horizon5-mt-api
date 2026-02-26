import uuid
from decimal import Decimal

from django.db import models

from app.models.base import BaseModel


class Strategy(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey("app.Account", on_delete=models.CASCADE, related_name="strategies")
    account_id: int
    symbol = models.CharField(max_length=50)
    prefix = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    magic_number = models.BigIntegerField(db_index=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))

    class Meta:
        db_table = "strategies"

    def __str__(self):
        return self.name
