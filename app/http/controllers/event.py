import base64
import json
from datetime import UTC, datetime
from typing import ClassVar

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ASCENDING, DESCENDING
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.collections.event import Event
from app.enums import EventStatus
from app.http.controllers.base import BaseController
from app.http.permissions.event import CanAckEvents, CanConsumeEvents, CanPushEvents, CanReadHistory, CanReadResponses
from app.http.requests.event.ack_event import AckEventRequestSerializer
from app.http.requests.event.push_event import PushEventRequestSerializer
from app.http.resources.event import EventResource
from app.models import Account


class EventController(BaseController):
    permission_map: ClassVar[dict] = {
        "push": [CanPushEvents],
        "consume": [CanConsumeEvents],
        "ack": [CanAckEvents],
        "history": [CanReadHistory],
        "response": [CanReadResponses],
    }
    default_permissions: ClassVar[list] = []

    @action(detail=False, methods=["post"], url_path="")
    def push(self, request, id):
        self._validate_account(id)
        serializer = PushEventRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event = Event.create(
            {
                "account_id": str(id),
                "user_id": str(request.user.id),
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
        return Response(EventResource(event).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="consume")
    def consume(self, request, id):
        try:
            limit = min(int(request.query_params.get("limit", 50)), 100)
        except (ValueError, TypeError):
            limit = 50
        consumer_id = str(request.user.id)
        now = datetime.now(UTC)

        consumed = []
        cursor = Event.where(
            {"account_id": str(id), "status": EventStatus.PENDING},
            sort=[("created_at", ASCENDING)],
            limit=limit,
        )
        for event in cursor:
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

        return Response(
            {
                "data": EventResource(consumed, many=True).data,
                "count": len(consumed),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="ack")
    def ack(self, request, id, eid):
        try:
            event_id = ObjectId(eid)
        except InvalidId:
            return Response({"detail": "Invalid event ID format."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AckEventRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        now = datetime.now(UTC)
        update_fields = {
            "status": EventStatus.PROCESSED,
            "processed_at": now,
            "updated_at": now,
        }
        response_data = serializer.validated_data.get("response")
        if response_data is not None:
            update_fields["response"] = response_data

        event = Event.find_one_and_update(
            {
                "_id": event_id,
                "account_id": str(id),
                "status": EventStatus.DELIVERED,
            },
            {"$set": update_fields},
            return_document=True,
        )
        if event is None:
            return Response(
                {"detail": "Event not found or not in delivered status."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EventResource(event).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request, id):
        try:
            limit = min(int(request.query_params.get("limit", 50)), 100)
        except (ValueError, TypeError):
            limit = 50
        raw_cursor = request.query_params.get("cursor")

        query: dict = {"account_id": str(id)}
        if raw_cursor:
            try:
                decoded = json.loads(base64.b64decode(raw_cursor).decode())
                cursor_created_at = datetime.fromisoformat(decoded["created_at"])
                cursor_id = ObjectId(decoded["_id"])
            except (ValueError, KeyError, TypeError, InvalidId):
                return Response({"detail": "Invalid cursor."}, status=status.HTTP_400_BAD_REQUEST)
            query["$or"] = [
                {"created_at": {"$lt": cursor_created_at}},
                {
                    "created_at": cursor_created_at,
                    "_id": {"$lt": cursor_id},
                },
            ]

        results = list(Event.where(query).sort([("created_at", DESCENDING), ("_id", DESCENDING)]).limit(limit + 1))

        has_more = len(results) > limit
        if has_more:
            results = results[:limit]

        next_cursor = None
        if has_more and results:
            last = results[-1]
            cursor_data = {
                "created_at": last["created_at"].isoformat(),
                "_id": str(last["_id"]),
            }
            next_cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()

        return Response(
            {
                "data": EventResource(results, many=True).data,
                "next_cursor": next_cursor,
                "has_more": next_cursor is not None,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["get"], url_path="response")
    def response(self, _request, id, eid):
        try:
            event_id = ObjectId(eid)
        except InvalidId:
            return Response({"detail": "Invalid event ID format."}, status=status.HTTP_400_BAD_REQUEST)

        event = Event.find_one(
            {
                "_id": event_id,
                "account_id": str(id),
            }
        )
        if event is None:
            return Response(
                {"detail": "Event not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if event.get("response") is None:
            return Response(
                {"detail": "No response available for this event."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"response": event["response"]},
            status=status.HTTP_200_OK,
        )

    def _validate_account(self, account_id):
        if not Account.objects.filter(id=account_id).exists():
            raise serializers.ValidationError({"detail": "Account not found."})
