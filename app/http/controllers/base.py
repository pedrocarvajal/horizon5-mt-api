from typing import ClassVar

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet


class BaseController(ViewSet):
    permission_map: ClassVar[dict] = {}
    throttle_map: ClassVar[dict] = {}
    default_permissions: ClassVar[list] = [IsAuthenticated]
    default_throttles: ClassVar[list | None] = None

    def get_permissions(self):
        permission_classes = self.permission_map.get(self.action, self.default_permissions)
        return [permission() for permission in permission_classes]

    def get_throttles(self):
        if self.action in self.throttle_map:
            return [throttle() for throttle in self.throttle_map[self.action]]
        if self.default_throttles is not None:
            return [throttle() for throttle in self.default_throttles]
        return super().get_throttles()
