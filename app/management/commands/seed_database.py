import os

from django.core.management.base import BaseCommand

from app.enums import SystemRole
from app.models.account import Account
from app.models.user import User

SEED_DATA = [
    {
        "email": "h5-api@mail.co",
        "password": os.environ.get("SEED_ROOT_PASSWORD", ""),
        "role": SystemRole.ROOT,
    },
    {
        "email": "h5-root@mail.co",
        "password": os.environ.get("SEED_ROOT_PASSWORD", ""),
        "role": SystemRole.ROOT,
    },
    {
        "email": "example-platform@mail.co",
        "password": os.environ.get("SEED_PLATFORM_PASSWORD", ""),
        "role": SystemRole.PLATFORM,
        "accounts": [200000001],
    },
    {
        "email": "example-producer@mail.co",
        "password": os.environ.get("SEED_PRODUCER_PASSWORD", ""),
        "role": SystemRole.PRODUCER,
        "accounts": [200000001],
    },
]


class Command(BaseCommand):
    help = "Seed database with initial users and accounts"

    def handle(self, *_args, **_options):
        for entry in SEED_DATA:
            user, created = User.objects.get_or_create(
                email=entry["email"],
                defaults={
                    "role": entry["role"],
                },
            )

            if created:
                user.set_password(entry["password"])
                user.save(update_fields=["password"])
                self.stdout.write(self.style.SUCCESS(f"Created user: {user.email}"))
            else:
                self.stdout.write(f"User already exists: {user.email}")

            for account_id in entry.get("accounts", []):
                _account, account_created = Account.objects.get_or_create(
                    id=account_id,
                    defaults={"user": user},
                )

                if account_created:
                    self.stdout.write(self.style.SUCCESS(f"  Created account: {account_id}"))
                else:
                    self.stdout.write(f"  Account already exists: {account_id}")

        self.stdout.write(self.style.SUCCESS("Seed completed"))
