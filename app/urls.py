from app.http.controllers.auth import AuthController
from app.http.controllers.event import EventController
from app.routing import Route

urlpatterns = Route.collect(
    Route.prefix("auth").group(
        Route.post("login/", AuthController, "login"),
    ),
    Route.prefix("accounts/<uuid:id>/events").group(
        Route.post("", EventController, "push"),
        Route.post("consume/", EventController, "consume"),
        Route.get("history/", EventController, "history"),
        Route.patch("<str:event_id>/ack/", EventController, "ack"),
        Route.get("<str:event_id>/response/", EventController, "event_response"),
    ),
)
