from django.urls import path

from app.http.controllers.auth import AuthController
from app.http.controllers.event import EventController

auth_login = AuthController.as_view({"post": "login"})
auth_me = AuthController.as_view({"get": "me"})

event_push = EventController.as_view({"post": "push"})
event_consume = EventController.as_view({"post": "consume"})
event_history = EventController.as_view({"get": "history"})
event_ack = EventController.as_view({"patch": "ack"})
event_response = EventController.as_view({"get": "event_response"})

urlpatterns = [
    path("auth/login/", auth_login),
    path("auth/me/", auth_me),
    path("accounts/<uuid:id>/events/", event_push),
    path("accounts/<uuid:id>/events/consume/", event_consume),
    path("accounts/<uuid:id>/events/history/", event_history),
    path("accounts/<uuid:id>/events/<str:event_id>/ack/", event_ack),
    path("accounts/<uuid:id>/events/<str:event_id>/response/", event_response),
]
