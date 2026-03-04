import json
import os
import time

from django.core.management.base import BaseCommand

from ._event_api_client import EventApiClient

MAX_POLL_ITERATIONS = 10
POLL_INTERVAL_SECONDS = 1


class BaseEventCommand(BaseCommand):
    def get_client(self) -> EventApiClient:
        api_key = os.environ.get("SEED_ROOT_API_KEY", "")
        base_url = os.environ.get("DJANGO_FORWARD_HOST", "http://localhost:8000")

        if not api_key:
            self.stderr.write(self.style.ERROR("API key required. Set $SEED_ROOT_API_KEY in .env"))
            raise SystemExit(1)

        return EventApiClient(base_url=base_url, api_key=api_key)

    def push_and_wait(self, client: EventApiClient, account_id: int, key: str, payload: dict) -> None:
        push_result = client.push_event(account_id, key, payload)
        event = push_result["data"]
        event_id = event["id"]

        self.stdout.write(f"\nEvent pushed  id={event_id}  key={event['key']}  status={event['status']}")
        self.stdout.write("Polling for response...\n")

        for attempt in range(1, MAX_POLL_ITERATIONS + 1):
            time.sleep(POLL_INTERVAL_SECONDS)
            result = client.poll_event_response(account_id, event_id)
            if result is not None:
                self.stdout.write(self.style.SUCCESS(f"Response received (attempt {attempt}/{MAX_POLL_ITERATIONS}):"))
                self.print_json(result["data"])
                return
            self.stdout.write(f"  [{attempt}/{MAX_POLL_ITERATIONS}] no response yet")

        self.stdout.write(self.style.WARNING(f"\nNo response after {MAX_POLL_ITERATIONS} attempts."))

    def print_json(self, data) -> None:
        self.stdout.write(json.dumps(data, indent=2))
