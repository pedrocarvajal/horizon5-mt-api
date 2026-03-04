from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand

EVENT_KEY = "post.order"


class Command(BaseEventCommand):
    help = "Push a post.order event to open a market or limit order"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")
        parser.add_argument("--symbol", type=str, default="XAUUSD", help="Trading symbol (default: XAUUSD)")
        parser.add_argument("--volume", type=float, default=0.01, help="Order volume in lots (default: 0.01)")
        parser.add_argument(
            "--type", type=str, choices=["buy", "sell"], default="buy", help="Order direction (default: buy)"
        )
        parser.add_argument("--strategy", type=int, required=True, help="Strategy ID")
        parser.add_argument("--price", type=float, default=None, help="Limit price (omit for market order)")
        parser.add_argument("--sl", type=float, default=None, help="Stop loss price")
        parser.add_argument("--tp", type=float, default=None, help="Take profit price")
        parser.add_argument("--comment", type=str, default=None, help="Order comment (max 255 chars)")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()

        payload: dict = {
            "symbol": options["symbol"],
            "strategy": options["strategy"],
            "type": options["type"],
            "volume": options["volume"],
        }

        if options["price"] is not None:
            payload["price"] = options["price"]
        if options["sl"] is not None:
            payload["stop_loss"] = options["sl"]
        if options["tp"] is not None:
            payload["take_profit"] = options["tp"]
        if options["comment"] is not None:
            payload["comment"] = options["comment"]

        self.stdout.write(f"Pushing {EVENT_KEY}: {payload}")
        self.push_and_wait(client, options["account_id"], EVENT_KEY, payload)
