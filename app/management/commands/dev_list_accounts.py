from ._base_event_command import BaseEventCommand


class Command(BaseEventCommand):
    help = "List all trading accounts (JSON output)"

    def handle(self, *_args, **_options) -> None:
        client = self.get_client()
        result = client.list_accounts()
        self.print_json(result)
