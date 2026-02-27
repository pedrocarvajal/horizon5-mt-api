from app.http.controllers.account import AccountController
from app.http.controllers.account_snapshot import AccountSnapshotController
from app.http.controllers.api_key import ApiKeyController
from app.http.controllers.auth import AuthController
from app.http.controllers.event import EventController
from app.http.controllers.heartbeat import HeartbeatController
from app.http.controllers.log import LogController
from app.http.controllers.media import MediaController
from app.http.controllers.order import OrderController
from app.http.controllers.strategy import StrategyController
from app.http.controllers.strategy_snapshot import StrategySnapshotController
from app.routing import Route

urlpatterns = Route.collect(
    Route.prefix("auth").group(
        Route.post("login/", AuthController, "login"),
        Route.post("refresh/", AuthController, "refresh"),
        Route.post("logout/", AuthController, "logout"),
        Route.get("me/", AuthController, "me"),
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
    Route.prefix("account/<int:id>/events").group(
        Route.post("", EventController, "push"),
        Route.post("consume/", EventController, "consume"),
        Route.get("history/", EventController, "history"),
    ),
    Route.prefix("account/<int:id>/event/<str:event_id>").group(
        Route.patch("ack/", EventController, "ack"),
        Route.get("response/", EventController, "response"),
    ),
    Route.prefix("account/<int:id>/media").group(
        Route.post("upload/", MediaController, "upload"),
        Route.get("<str:file_name>/download/", MediaController, "download"),
        Route.delete("<str:file_name>/", MediaController, "destroy"),
    ),
    Route.prefix("account").group(
        Route.post("", AccountController, "upsert"),
    ),
    Route.prefix("strategy").group(
        Route.post("", StrategyController, "upsert"),
    ),
    Route.prefix("heartbeat").group(
        Route.post("", HeartbeatController, "store"),
    ),
    Route.prefix("order").group(
        Route.post("", OrderController, "upsert"),
    ),
    Route.prefix("log").group(
        Route.post("", LogController, "store"),
    ),
    Route.prefix("account-snapshot").group(
        Route.post("", AccountSnapshotController, "store"),
    ),
    Route.prefix("strategy-snapshot").group(
        Route.post("", StrategySnapshotController, "store"),
    ),
)
