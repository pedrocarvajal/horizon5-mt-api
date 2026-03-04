from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand


class Command(BaseEventCommand):
    help = "List trading strategies with optional filters (JSON output)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, default=None, help="Filter by MetaTrader account ID")
        parser.add_argument("--symbol", type=str, default=None, help="Filter by symbol (e.g. XAUUSD)")
        parser.add_argument("--name", type=str, default=None, help="Filter by strategy name (case-insensitive)")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()
        result = client.list_strategies()
        strategies = result.get("data", [])

        account_id = options["account_id"]
        symbol = options["symbol"]
        name = options["name"]

        if account_id is not None:
            strategies = [s for s in strategies if s.get("account_id") == account_id]
        if symbol is not None:
            strategies = [s for s in strategies if s.get("symbol", "").upper() == symbol.upper()]
        if name is not None:
            name_lower = name.lower()
            strategies = [s for s in strategies if name_lower in s.get("name", "").lower()]

        self.print_json({"data": strategies, "meta": {"count": len(strategies)}})
