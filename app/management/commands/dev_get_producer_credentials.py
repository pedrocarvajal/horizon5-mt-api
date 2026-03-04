from django.core.management.base import BaseCommand

from app.enums import SystemRole
from app.models.api_key import ApiKey
from app.models.user import User


class Command(BaseCommand):
    help = "Get or create producer credentials (user + API key)"

    def handle(self, *_args, **_options) -> None:
        email = input("Email: ").strip()

        if not email:
            self.stderr.write(self.style.ERROR("Email is required"))
            return

        try:
            user = User.objects.get(email=email)
            self._handle_existing_user(user)

        except User.DoesNotExist:
            self._handle_new_user(email)

    def _handle_existing_user(self, user: User) -> None:
        self.stdout.write(f"\nUser found: {user.email} ({user.role})")

        allowed_ips = self._prompt_allowed_ips()
        raw_key = self._create_api_key(user, allowed_ips)

        self._print_credentials(user.email, None, raw_key, allowed_ips)

    def _handle_new_user(self, email: str) -> None:
        self.stdout.write(f"\nNo user found with email: {email}")
        self.stdout.write("Creating new producer...\n")

        password = input("Password: ").strip()

        if not password:
            self.stderr.write(self.style.ERROR("Password is required"))
            return

        allowed_ips = self._prompt_allowed_ips()
        user = User.objects.create_user(
            email=email,
            password=password,
            role=SystemRole.PRODUCER,
        )

        raw_key = self._create_api_key(user, allowed_ips)
        self._print_credentials(email, password, raw_key, allowed_ips)

    def _prompt_allowed_ips(self) -> list[str]:
        allowed_ip = input("IP to register for API key (leave empty for any): ").strip()

        return [allowed_ip] if allowed_ip else []

    def _create_api_key(self, user: User, allowed_ips: list[str]) -> str:
        raw_key, key_hash = ApiKey.generate_key()
        ApiKey.objects.create(
            user=user,
            name=f"producer-cli-{user.email}",
            key_hash=key_hash,
            prefix=raw_key[: ApiKey.PREFIX_LENGTH],
            allowed_ips=allowed_ips,
        )

        return raw_key

    def _print_credentials(
        self,
        email: str,
        password: str | None,
        api_key: str,
        allowed_ips: list[str],
    ) -> None:
        separator = "=" * 50
        self.stdout.write(f"\n{separator}")
        self.stdout.write(self.style.SUCCESS("  PRODUCER CREDENTIALS"))
        self.stdout.write(separator)
        self.stdout.write(f"  Email:       {email}")

        if password:
            self.stdout.write(f"  Password:    {password}")
        else:
            self.stdout.write("  Password:    (unchanged)")

        self.stdout.write(f"  API Key:     {api_key}")
        self.stdout.write(f"  Allowed IPs: {allowed_ips if allowed_ips else 'any'}")
        self.stdout.write(f"{separator}\n")
