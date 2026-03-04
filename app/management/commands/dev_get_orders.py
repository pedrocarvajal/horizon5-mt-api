from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand

EVENT_KEY = "get.orders"


class Command(BaseEventCommand):
    help = "Push a get.orders event to retrieve orders from MT with optional filters"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")
        parser.add_argument("--strategy", type=int, required=True, help="Strategy magic number")
        parser.add_argument("--symbol", type=str, default=None, help="Filter by symbol (e.g. XAUUSD)")
        parser.add_argument("--side", type=str, choices=["buy", "sell"], default=None, help="Filter by side")
        parser.add_argument(
            "--status",
            type=str,
            choices=["pending", "open", "closing", "closed", "cancelled"],
            default=None,
            help="Filter by order status",
        )

    def handle(self, *_args, **options) -> None:
        client = self.get_client()

        payload: dict = {"strategy": options["strategy"]}

        if options["symbol"] is not None:
            payload["symbol"] = options["symbol"]
        if options["side"] is not None:
            payload["side"] = options["side"]
        if options["status"] is not None:
            payload["status"] = options["status"]

        self.stdout.write(f"Pushing {EVENT_KEY}: {payload}")
        self.push_and_wait(client, options["account_id"], EVENT_KEY, payload)
