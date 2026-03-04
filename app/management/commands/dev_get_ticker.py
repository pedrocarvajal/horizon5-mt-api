from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand

EVENT_KEY = "get.ticker"


class Command(BaseEventCommand):
    help = "Push a get.ticker event to retrieve tick data for one or more symbols"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")
        parser.add_argument(
            "--symbols",
            type=str,
            default="XAUUSD",
            help="Comma-separated trading symbols (default: XAUUSD)",
        )

    def handle(self, *_args, **options) -> None:
        client = self.get_client()
        payload = {"symbols": options["symbols"]}
        self.stdout.write(f"Pushing {EVENT_KEY}: {payload}")
        self.push_and_wait(client, options["account_id"], EVENT_KEY, payload)
