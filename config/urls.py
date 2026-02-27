from app.routing import Route

urlpatterns = Route.collect(
    Route.prefix("api/v1").include("app.urls"),
)
