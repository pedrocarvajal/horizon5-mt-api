from django.contrib import admin
from django.urls import include, path

from app.http.controllers.health import HealthController

health_check = HealthController.as_view({"get": "check"})
health_detailed = HealthController.as_view({"get": "detailed"})

urlpatterns = [
    path("health/", health_check),
    path("health/detailed/", health_detailed),
    path("api/v1/", include("app.urls")),
    path("admin/", admin.site.urls),
]
