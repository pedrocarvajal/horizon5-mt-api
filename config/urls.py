from app.http.controllers.health import HealthController
from app.routing import Route

urlpatterns = Route.collect(
    Route.get("health/", HealthController, "check"),
    Route.prefix("api/v1").include("app.urls"),
)
