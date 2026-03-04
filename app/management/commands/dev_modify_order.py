from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand

EVENT_KEY = "put.order"


class Command(BaseEventCommand):
    help = "Push a put.order event to modify stop loss / take profit on an open order"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")
        parser.add_argument("--order-id", type=int, required=True, help="Order ticket to modify")
        parser.add_argument("--sl", type=float, default=None, help="New stop loss price")
        parser.add_argument("--tp", type=float, default=None, help="New take profit price")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()

        payload: dict = {"id": options["order_id"]}

        if options["sl"] is not None:
            payload["stop_loss"] = options["sl"]
        if options["tp"] is not None:
            payload["take_profit"] = options["tp"]

        self.stdout.write(f"Pushing {EVENT_KEY}: {payload}")
        self.push_and_wait(client, options["account_id"], EVENT_KEY, payload)
