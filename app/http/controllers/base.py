from abc import abstractmethod
from typing import Any, ClassVar

from pymongo import ASCENDING, DESCENDING
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.collections.base import BaseDocument
from app.http.requests.list_request import ListRequestSerializer
from app.http.response import build_response


class BaseController(ViewSet):
    permissions: ClassVar[dict[str, list[type]]] = {}
    throttles: ClassVar[dict[str, list[type]]] = {}
    default_permissions: ClassVar[list[type]] = [IsAuthenticated]

    def get_permissions(self) -> list:
        permission_classes = self.permissions.get(self.action, self.default_permissions)
        return [permission() for permission in permission_classes]

    def get_throttles(self) -> list:
        if self.action in self.throttles:
            return [throttle() for throttle in self.throttles[self.action]]

        return super().get_throttles()

    def reply(
        self,
        message: str | None = None,
        data: Any = None,
        status_code: int = http_status.HTTP_200_OK,
        meta: dict[str, Any] | None = None,
    ) -> Response:
        return build_response(
            message=message,
            data=data,
            status_code=status_code,
            meta=meta,
        )


class PaginatedController(BaseController):
    collection: ClassVar[type[BaseDocument]]
    list_serializer_class: ClassVar[type[ListRequestSerializer]]
    orderable_columns: ClassVar[list[str]] = []
    filterable_columns: ClassVar[list[str]] = []
    integer_columns: ClassVar[set[str]] = set()
    float_columns: ClassVar[set[str]] = set()

    @abstractmethod
    def get_base_query(self, validated: dict) -> dict: ...

    @abstractmethod
    def serialize_document(self, document: dict) -> dict: ...

    def get_serializer_context(self) -> dict:
        return {
            "orderable_columns": self.orderable_columns,
            "filterable_columns": self.filterable_columns,
            "integer_columns": self.integer_columns,
            "float_columns": self.float_columns,
        }

    @action(detail=False, methods=["get"], url_path="")
    def index(self, request: Request) -> Response:
        serializer = self.list_serializer_class(data=request.query_params, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        page = validated["page"]
        per_page = validated["per_page"]
        offset = (page - 1) * per_page

        query = self.get_base_query(validated)

        if "filter_by" in validated and "filter_value" in validated:
            query[validated["filter_by"]] = serializer.get_cast_filter_value(
                validated["filter_by"], validated["filter_value"]
            )

        order_by = validated["order_by"]

        if order_by.startswith("-"):
            sort_field = order_by[1:]
            sort_direction = DESCENDING
        else:
            sort_field = order_by
            sort_direction = ASCENDING

        total = self.collection.count(query)

        documents = list(
            self.collection.where(query)
            .sort([(sort_field, sort_direction), ("_id", DESCENDING)])
            .skip(offset)
            .limit(per_page)
        )

        data = [self.serialize_document(document) for document in documents]

        return self.reply(
            data=data,
            meta={
                "count": len(data),
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
                },
                "filterable_columns": list(self.filterable_columns),
                "orderable_columns": list(self.orderable_columns),
            },
        )
