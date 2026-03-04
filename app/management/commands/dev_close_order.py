from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand

EVENT_KEY = "delete.order"


class Command(BaseEventCommand):
    help = "Push a delete.order event to close an open position"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")
        parser.add_argument("--order-id", type=str, required=True, help="Order ID (UUID) to close")
        parser.add_argument("--strategy", type=int, required=True, help="Strategy ID")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()

        payload = {
            "id": options["order_id"],
            "strategy": options["strategy"],
        }

        self.stdout.write(f"Pushing {EVENT_KEY}: {payload}")
        self.push_and_wait(client, options["account_id"], EVENT_KEY, payload)
