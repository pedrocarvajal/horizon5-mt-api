import csv
import io
import time

from django.core.management.base import CommandParser

from ._base_event_command import MAX_POLL_ITERATIONS, POLL_INTERVAL_SECONDS, BaseEventCommand

EVENT_KEY = "get.klines"
MIN_CSV_ROWS_WITH_HEADER = 2


class Command(BaseEventCommand):
    help = "Push a get.klines event to retrieve historical candlestick data"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--account-id", type=int, required=True, help="MetaTrader account ID")
        parser.add_argument("--symbol", type=str, default="XAUUSD", help="Trading symbol (default: XAUUSD)")
        parser.add_argument(
            "--timeframe", type=str, default="D1", help="Timeframe: M1,M5,M15,M30,H1,H4,D1,W1,MN1 (default: D1)"
        )
        parser.add_argument("--from-date", type=str, required=True, help="Start date (YYYY-MM-DD)")
        parser.add_argument("--to-date", type=str, required=True, help="End date (YYYY-MM-DD)")

    def handle(self, *_args, **options) -> None:
        client = self.get_client()
        account_id = options["account_id"]
        payload = {
            "symbol": options["symbol"],
            "timeframe": options["timeframe"],
            "from_date": options["from_date"],
            "to_date": options["to_date"],
        }

        self.stdout.write(f"Pushing {EVENT_KEY}: {payload}")

        push_result = client.push_event(account_id, EVENT_KEY, payload)
        event = push_result["data"]
        event_id = event["id"]

        self.stdout.write(f"\nEvent pushed  id={event_id}  key={event['key']}  status={event['status']}")
        self.stdout.write("Polling for response...\n")

        response_data = None
        for attempt in range(1, MAX_POLL_ITERATIONS + 1):
            time.sleep(POLL_INTERVAL_SECONDS)
            result = client.poll_event_response(account_id, event_id)
            if result is not None:
                self.stdout.write(self.style.SUCCESS(f"Response received (attempt {attempt}/{MAX_POLL_ITERATIONS}):"))
                response_data = result["data"]["response"]
                self.print_json(response_data)
                break
            self.stdout.write(f"  [{attempt}/{MAX_POLL_ITERATIONS}] no response yet")

        if response_data is None:
            self.stdout.write(self.style.WARNING(f"\nNo response after {MAX_POLL_ITERATIONS} attempts."))
            return

        if response_data.get("status") != "success":
            self.stdout.write(self.style.ERROR("\nEvent completed with error."))
            return

        file_name = response_data.get("file_name", "")
        row_count = response_data.get("rows", 0)

        self.stdout.write(f"\nDownloading klines CSV: {file_name} ({row_count} rows)")

        csv_bytes = client.download_media(account_id, file_name)
        reader = csv.reader(io.StringIO(csv_bytes.decode("utf-8")))
        rows = list(reader)

        if len(rows) < MIN_CSV_ROWS_WITH_HEADER:
            self.stdout.write(self.style.WARNING("CSV is empty or has no data rows."))
            return

        header = rows[0]
        data_rows = rows[1:]
        preview_count = 3

        self.stdout.write(self.style.SUCCESS(f"\nKlines loaded: {len(data_rows)} rows"))
        self.stdout.write(f"Columns: {', '.join(header)}\n")

        self.stdout.write(self.style.SUCCESS(f"First {min(preview_count, len(data_rows))} rows:"))
        for row in data_rows[:preview_count]:
            self.stdout.write(f"  {', '.join(row)}")

        if len(data_rows) > preview_count * 2:
            self.stdout.write(f"  ... ({len(data_rows) - preview_count * 2} more rows)")

        if len(data_rows) > preview_count:
            self.stdout.write(self.style.SUCCESS(f"\nLast {min(preview_count, len(data_rows))} rows:"))
            for row in data_rows[-preview_count:]:
                self.stdout.write(f"  {', '.join(row)}")
