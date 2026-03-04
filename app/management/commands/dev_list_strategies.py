from ._base_event_command import BaseEventCommand


class Command(BaseEventCommand):
    help = "List all trading strategies (JSON output)"

    def handle(self, *_args, **_options) -> None:
        client = self.get_client()
        result = client.list_strategies()
        self.print_json(result)
