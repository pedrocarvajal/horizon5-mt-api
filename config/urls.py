from django.urls import include, path

from app.http.controllers.health import HealthController

health_check = HealthController.as_view({"get": "check"})

urlpatterns = [
    path("health/", health_check),
    path("api/v1/", include("app.urls")),
]
