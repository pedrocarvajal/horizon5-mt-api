from typing import Any, ClassVar

from django.utils import timezone
from pymongo import ASCENDING, DESCENDING
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.event import Event
from app.enums import EventKey, EventStatus
from app.http.controllers.base import BaseController
from app.http.permissions.event import CanAckEvents, CanConsumeEvents, CanPushEvents, CanReadHistory, CanReadResponses
from app.http.requests.event.ack_event import AckEventRequestSerializer
from app.http.requests.event.consume_event import ConsumeEventRequestSerializer
from app.http.requests.event.event_response import EventResponseRequestSerializer
from app.http.requests.event.history_event import HistoryEventRequestSerializer
from app.http.requests.event.push_event import PushEventRequestSerializer
from app.http.resources.event import EventResource
from app.models import Account


class EventController(BaseController):
    permissions: ClassVar[dict] = {
        "keys": [IsAuthenticated],
        "push": [CanPushEvents],
        "consume": [CanConsumeEvents],
        "ack": [CanAckEvents],
        "history": [CanReadHistory],
        "response": [CanReadResponses],
    }

    @action(detail=False, methods=["get"], url_path="keys")
    def keys(self, _request: Request) -> Response:
        data = [
            {
                "key": event_key.value,
                "name": event_key.name,
                "schema": event_key.schema(),
            }
            for event_key in EventKey
        ]

        return self.reply(data=data)

    @action(detail=False, methods=["post"], url_path="")
    def push(self, request: Request, id: int) -> Response:
        self._validate_account(id)
        serializer = PushEventRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = Event.create(
            {
                "account_id": id,
                "user_id": str(request.user.pk),
                "consumer_id": None,
                "key": str(serializer.validated_data["key"]),
                "payload": serializer.validated_data["payload"],
                "response": None,
                "status": EventStatus.PENDING,
                "delivered_at": None,
                "processed_at": None,
                "attempts": 0,
            }
        )

        return self.reply(
            data=EventResource(event).data,
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="consume")
    def consume(self, request: Request, id: int) -> Response:
        self._validate_account(id)
        serializer = ConsumeEventRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        limit = serializer.validated_data["limit"]
        consumer_id = str(request.user.pk)
        now = timezone.now()
        consumed: list[dict] = []

        query: dict[str, Any] = {"account_id": id, "status": EventStatus.PENDING}

        if "key" in serializer.validated_data:
            keys = serializer.validated_data["key"]
            query["key"] = keys[0] if len(keys) == 1 else {"$in": keys}

        cursor = Event.where(
            query,
            sort=[("created_at", ASCENDING)],
        )

        for event in cursor:
            if len(consumed) >= limit:
                break

            result = Event.find_one_and_update(
                {"_id": event["_id"], "status": EventStatus.PENDING},
                {
                    "$set": {
                        "status": EventStatus.DELIVERED,
                        "consumer_id": consumer_id,
                        "delivered_at": now,
                        "updated_at": now,
                    },
                    "$inc": {"attempts": 1},
                },
                return_document=True,
            )

            if result:
                consumed.append(result)

        return self.reply(
            data=EventResource(consumed, many=True).data,
            meta={"count": len(consumed)},
        )

    @action(detail=True, methods=["patch"], url_path="ack")
    def ack(self, request: Request, id: int, event_id: str) -> Response:
        serializer = AckEventRequestSerializer(data={**request.data, "event_id": event_id})
        serializer.is_valid(raise_exception=True)

        response_data = serializer.validated_data.get("response")
        event_id = serializer.validated_data["event_id"]
        now = timezone.now()

        update_fields = {
            "status": EventStatus.PROCESSED,
            "processed_at": now,
            "updated_at": now,
        }

        if response_data is not None:
            update_fields["response"] = response_data

        event = Event.find_one_and_update(
            {
                "_id": event_id,
                "account_id": id,
                "status": EventStatus.DELIVERED,
            },
            {"$set": update_fields},
            return_document=True,
        )

        if event is None:
            return self.reply(
                message="Event not found or not in delivered status.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return self.reply(
            data=EventResource(event).data,
        )

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request: Request, id: int) -> Response:
        self._validate_account(id)
        serializer = HistoryEventRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        limit = serializer.validated_data["limit"]
        query: dict[str, Any] = {"account_id": id}

        if "status" in serializer.validated_data:
            query["status"] = serializer.validated_data["status"]

        if "key" in serializer.validated_data:
            query["key"] = serializer.validated_data["key"]

        events = list(Event.where(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).limit(limit))

        return self.reply(
            data=EventResource(events, many=True).data,
        )

    @action(detail=True, methods=["get"], url_path="response")
    def response(self, _request: Request, id: int, event_id: str) -> Response:
        self._validate_account(id)
        serializer = EventResponseRequestSerializer(data={"event_id": event_id})
        serializer.is_valid(raise_exception=True)

        event_id = serializer.validated_data["event_id"]

        event = Event.find_one(
            {
                "_id": event_id,
                "account_id": id,
            }
        )

        if event is None:
            return self.reply(
                message="Event not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if event.get("response") is None:
            return self.reply(
                message="No response available for this event.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return self.reply(
            data={"response": event["response"]},
        )

    def _validate_account(self, account_id: int) -> None:
        if not Account.objects.filter(id=account_id).exists():
            raise serializers.ValidationError({"detail": "Account not found."})
