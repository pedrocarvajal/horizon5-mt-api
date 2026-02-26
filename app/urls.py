from app.http.controllers.api_key import ApiKeyController
from app.http.controllers.auth import AuthController
from app.http.controllers.event import EventController
from app.http.controllers.media import MediaController
from app.routing import Route

urlpatterns = Route.collect(
    Route.prefix("auth").group(
        Route.post("login/", AuthController, "login"),
    ),
    Route.prefix("api-keys").group(
        Route.get("", ApiKeyController, "index"),
    ),
    Route.prefix("api-key").group(
        Route.post("", ApiKeyController, "store"),
        Route.get("<uuid:id>/", ApiKeyController, "show"),
        Route.patch("<uuid:id>/", ApiKeyController, "update"),
        Route.delete("<uuid:id>/", ApiKeyController, "destroy"),
    ),
    Route.prefix("events").group(
        Route.get("keys/", EventController, "keys"),
    ),
    Route.prefix("account/<uuid:id>/events").group(
        Route.post("", EventController, "push"),
        Route.post("consume/", EventController, "consume"),
        Route.get("history/", EventController, "history"),
    ),
    Route.prefix("account/<uuid:id>/event/<str:event_id>").group(
        Route.patch("ack/", EventController, "ack"),
        Route.get("response/", EventController, "response"),
    ),
    Route.prefix("account/<uuid:id>/media").group(
        Route.post("upload/", MediaController, "upload"),
        Route.get("<str:file_name>/download/", MediaController, "download"),
        Route.delete("<str:file_name>/", MediaController, "destroy"),
    ),
)
