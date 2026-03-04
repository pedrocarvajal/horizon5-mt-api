from django.core.management.base import CommandParser

from ._base_event_command import BaseEventCommand


class Command(BaseEventCommand):
    help = "List account or strategy snapshots (JSON output)"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--type", type=str, choices=["account", "strategy"], required=True, help="Snapshot type")
        parser.add_argument("--account-id", type=int, default=None, help="Account ID (required for account type)")
        parser.add_argument("--strategy-id", type=str, default=None, help="Strategy UUID (required for strategy type)")
        parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
        parser.add_argument("--per-page", type=int, default=50, help="Items per page (default: 50)")
        parser.add_argument("--order-by", type=str, default="-created_at", help="Sort column (default: -created_at)")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()
        snapshot_type = options["type"]

        if snapshot_type == "account":
            if options["account_id"] is None:
                self.stderr.write(self.style.ERROR("--account-id is required for --type account"))
                raise SystemExit(1)
            result = client.list_account_snapshots(
                account_id=options["account_id"],
                page=options["page"],
                per_page=options["per_page"],
                order_by=options["order_by"],
            )

        else:
            if options["strategy_id"] is None:
                self.stderr.write(self.style.ERROR("--strategy-id is required for --type strategy"))
                raise SystemExit(1)
            result = client.list_strategy_snapshots(
                strategy_id=options["strategy_id"],
                account_id=options["account_id"],
                page=options["page"],
                per_page=options["per_page"],
                order_by=options["order_by"],
            )

        self.print_json(result)
