import json
import os
import time

import requests
from django.core.management.base import BaseCommand

from ._event_api_client import EventApiClient

MAX_POLL_ITERATIONS = 60
POLL_INTERVAL_SECONDS = 1


class BaseEventCommand(BaseCommand):
    def execute(self, *args, **options):
        try:
            super().execute(*args, **options)
        except requests.HTTPError as error:
            try:
                body = json.dumps(error.response.json(), indent=2)
            except Exception:
                body = error.response.text if error.response else str(error)
            self.stderr.write(self.style.ERROR(f"API Error {error.response.status_code}: {body}"))
            raise SystemExit(1) from None
        except PermissionError as error:
            self.stderr.write(self.style.ERROR(str(error)))
            raise SystemExit(1) from None

    def get_client(self) -> EventApiClient:
        email = os.environ.get("SEED_ROOT_EMAIL", "")
        password = os.environ.get("SEED_ROOT_PASSWORD", "")
        base_url = os.environ.get("DJANGO_FORWARD_HOST", "http://localhost:8000")

        if not email or not password:
            self.stderr.write(
                self.style.ERROR("Credentials required. Set $SEED_ROOT_EMAIL and $SEED_ROOT_PASSWORD in .env")
            )
            raise SystemExit(1)

        return EventApiClient(base_url=base_url, email=email, password=password)

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
