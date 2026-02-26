from django.urls import path

from app.http.controllers.api_key import ApiKeyController
from app.http.controllers.auth import AuthController
from app.http.controllers.event import EventController
from app.http.controllers.media import MediaController
from app.routing import Route

urlpatterns = Route.collect(
    Route.prefix("auth").group(
        Route.post("login/", AuthController, "login"),
    ),
    path("api-keys/", ApiKeyController.as_view({"get": "list", "post": "create"})),
    Route.prefix("api-keys").group(
        Route.get("<uuid:api_key_id>/", ApiKeyController, "show"),
        Route.patch("<uuid:api_key_id>/", ApiKeyController, "update"),
        Route.delete("<uuid:api_key_id>/", ApiKeyController, "destroy"),
    ),
    Route.prefix("events").group(
        Route.get("keys/", EventController, "keys"),
    ),
    Route.prefix("accounts/<uuid:id>/events").group(
        Route.post("", EventController, "push"),
        Route.post("consume/", EventController, "consume"),
        Route.get("history/", EventController, "history"),
        Route.patch("<str:event_id>/ack/", EventController, "ack"),
        Route.get("<str:event_id>/response/", EventController, "event_response"),
    ),
    Route.prefix("accounts/<uuid:id>/media").group(
        Route.post("upload/", MediaController, "upload"),
        Route.get("<str:file_name>/download/", MediaController, "download"),
        Route.delete("<str:file_name>/", MediaController, "destroy"),
    ),
)
