import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_account_pk_and_trading_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Strategy",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("symbol", models.CharField(max_length=50)),
                ("prefix", models.CharField(max_length=50)),
                ("name", models.CharField(max_length=255)),
                ("magic_number", models.BigIntegerField(db_index=True)),
                ("balance", models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="strategies",
                        to="app.account",
                    ),
                ),
            ],
            options={
                "db_table": "strategies",
            },
        ),
    ]
