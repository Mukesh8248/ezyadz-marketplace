from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/<int:service_id>/",
        views.create_booking_view,
        name="create_booking",
    ),
    path(
        "history/",
        views.booking_history_view,
        name="booking_history",
    ),
    path(
        "<int:pk>/status/<str:status>/",
        views.update_booking_status_view,
        name="update_booking_status",
    ),
]