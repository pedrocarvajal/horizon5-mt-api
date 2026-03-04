from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand

EVENT_KEY = "get.account.info"


class Command(BaseEventCommand):
    help = "Push a get.account.info event to retrieve live account details from MT"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()
        self.stdout.write(f"Pushing {EVENT_KEY}")
        self.push_and_wait(client, options["account_id"], EVENT_KEY, {})
