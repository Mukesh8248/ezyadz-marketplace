from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.service_list_view,
        name="service_list",
    ),

    path(
        "add/",
        views.add_service_view,
        name="add_service",
    ),

    path(
        "<int:pk>/",
        views.service_detail_view,
        name="service_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.edit_service_view,
        name="edit_service",
    ),

    path(
        "<int:pk>/delete/",
        views.delete_service_view,
        name="delete_service",
    ),

    path(
        "<int:pk>/toggle-availability/",
        views.toggle_service_availability_view,
        name="toggle_service_availability",
    ),

    path(
        "images/<int:image_id>/delete/",
        views.delete_service_image_view,
        name="delete_service_image",
    ),
]