from __future__ import annotations

from typing import Any

from django.urls import URLPattern, URLResolver, include, path
from rest_framework.viewsets import ViewSetMixin


class RouteDefinition:
    def __init__(self, method: str, route_path: str, controller: type[ViewSetMixin], action: str) -> None:
        self.method = method
        self.route_path = route_path
        self.controller = controller
        self.action = action
        self.route_name: str | None = None

    def name(self, route_name: str) -> RouteDefinition:
        self.route_name = route_name

        return self

    def resolve(self, prefix: str = "", name_prefix: str = "") -> URLPattern:
        full_path = prefix + self.route_path
        view = self.controller.as_view({self.method: self.action})
        kwargs: dict[str, Any] = {"route": full_path, "view": view}

        if self.route_name:
            kwargs["name"] = name_prefix + self.route_name

        return path(**kwargs)


class MatchDefinition:
    def __init__(self, actions: dict[str, Any], route_path: str, controller: type[ViewSetMixin]) -> None:
        self.actions = actions
        self.route_path = route_path
        self.controller = controller
        self.route_name: str | None = None

    def name(self, route_name: str) -> MatchDefinition:
        self.route_name = route_name

        return self

    def resolve(self, prefix: str = "", name_prefix: str = "") -> URLPattern:
        full_path = prefix + self.route_path
        view = self.controller.as_view(self.actions)
        kwargs: dict[str, Any] = {"route": full_path, "view": view}

        if self.route_name:
            kwargs["name"] = name_prefix + self.route_name

        return path(**kwargs)


class IncludeDefinition:
    def __init__(self, module: str, prefix: str = "", name_prefix: str = "") -> None:
        self.module = module
        self.route_name: str | None = None
        self._prefix = prefix
        self._name_prefix = name_prefix

    def name(self, route_name: str) -> IncludeDefinition:
        self.route_name = route_name
        return self

    def resolve(self, prefix: str = "", name_prefix: str = "") -> URLResolver:
        resolved_prefix = prefix if prefix else self._prefix
        resolved_name_prefix = name_prefix if name_prefix else self._name_prefix
        full_name = (resolved_name_prefix + self.route_name) if self.route_name else None
        included = include((self.module, full_name)) if full_name else include(self.module)

        return path(resolved_prefix, included)


class RouteRegistrar:
    def __init__(self, prefix: str = "", name_prefix: str = "") -> None:
        self._prefix = prefix
        self._name_prefix = name_prefix

    def prefix(self, segment: str) -> RouteRegistrar:
        combined = self._prefix + segment.strip("/")

        if segment and not segment.endswith("/"):
            combined += "/"

        return RouteRegistrar(prefix=combined, name_prefix=self._name_prefix)

    def name(self, name_segment: str) -> RouteRegistrar:
        return RouteRegistrar(prefix=self._prefix, name_prefix=self._name_prefix + name_segment)

    def group(
        self, *routes: RouteDefinition | MatchDefinition | IncludeDefinition | list
    ) -> list[URLPattern | URLResolver]:
        resolved = []

        for route in routes:
            if isinstance(route, list):
                resolved.extend(route)

            elif isinstance(route, (RouteDefinition, MatchDefinition, IncludeDefinition)):
                resolved.append(route.resolve(self._prefix, self._name_prefix))

            else:
                resolved.append(route)

        return resolved

    def include(self, module: str) -> IncludeDefinition:
        return IncludeDefinition(module, prefix=self._prefix, name_prefix=self._name_prefix)


class Route:
    @staticmethod
    def _route(method: str, route_path: str, controller: type[ViewSetMixin], action: str) -> RouteDefinition:
        return RouteDefinition(method, route_path, controller, action)

    @staticmethod
    def get(route_path: str, controller: type[ViewSetMixin], action: str) -> RouteDefinition:
        return Route._route("get", route_path, controller, action)

    @staticmethod
    def post(route_path: str, controller: type[ViewSetMixin], action: str) -> RouteDefinition:
        return Route._route("post", route_path, controller, action)

    @staticmethod
    def put(route_path: str, controller: type[ViewSetMixin], action: str) -> RouteDefinition:
        return Route._route("put", route_path, controller, action)

    @staticmethod
    def patch(route_path: str, controller: type[ViewSetMixin], action: str) -> RouteDefinition:
        return Route._route("patch", route_path, controller, action)

    @staticmethod
    def delete(route_path: str, controller: type[ViewSetMixin], action: str) -> RouteDefinition:
        return Route._route("delete", route_path, controller, action)

    @staticmethod
    def match(actions: dict[str, Any], route_path: str, controller: type[ViewSetMixin]) -> MatchDefinition:
        return MatchDefinition(actions, route_path, controller)

    @staticmethod
    def prefix(segment: str) -> RouteRegistrar:
        return RouteRegistrar().prefix(segment)

    @staticmethod
    def name(name_segment: str) -> RouteRegistrar:
        return RouteRegistrar().name(name_segment)

    @staticmethod
    def group(*routes: RouteDefinition | MatchDefinition | IncludeDefinition | list) -> list[URLPattern | URLResolver]:
        return RouteRegistrar().group(*routes)

    @staticmethod
    def include(module: str) -> IncludeDefinition:
        return IncludeDefinition(module)

    @staticmethod
    def collect(
        *items: RouteDefinition | MatchDefinition | IncludeDefinition | URLPattern | URLResolver | list,
    ) -> list[URLPattern | URLResolver]:
        collected = []

        for item in items:
            if isinstance(item, list):
                collected.extend(item)

            elif isinstance(item, (RouteDefinition, MatchDefinition, IncludeDefinition)):
                collected.append(item.resolve())

            else:
                collected.append(item)

        return collected
