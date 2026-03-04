import os

from django.core.management.base import BaseCommand

from app.enums import SystemRole
from app.models.account import Account
from app.models.api_key import ApiKey
from app.models.user import User

SEED_DATA = [
    {
        "email": "pedro@mail.co",
        "password": os.environ.get("SEED_ROOT_PASSWORD", ""),
        "role": SystemRole.ROOT,
        "api_keys": [
            {
                "name": "root",
                "raw_key": os.environ.get("SEED_ROOT_API_KEY", ""),
            },
        ],
    },
    {
        "email": "horizon5@mail.co",
        "password": os.environ.get("SEED_ROOT_PASSWORD", ""),
        "role": SystemRole.ROOT,
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

            for api_key_entry in entry.get("api_keys", []):
                raw_key = api_key_entry["raw_key"]

                if not raw_key:
                    self.stdout.write(self.style.WARNING("  Skipping API key: SEED_ROOT_API_KEY not set"))
                    continue

                key_hash = ApiKey.hash_key(raw_key)
                _api_key, key_created = ApiKey.objects.get_or_create(
                    key_hash=key_hash,
                    defaults={
                        "user": user,
                        "name": api_key_entry["name"],
                        "prefix": raw_key[: ApiKey.PREFIX_LENGTH],
                    },
                )

                if key_created:
                    self.stdout.write(self.style.SUCCESS(f"  Created API key: {api_key_entry['name']}"))
                else:
                    self.stdout.write(f"  API key already exists: {api_key_entry['name']}")

        self.stdout.write(self.style.SUCCESS("Seed completed"))
