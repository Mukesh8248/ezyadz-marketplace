from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (
    BookingCreateAPIView,
    BookingHistoryAPIView,
    LoginAPIView,
    RegisterAPIView,
    ServiceListAPIView,
)

urlpatterns = [
    path(
        "register/",
        RegisterAPIView.as_view(),
        name="api_register",
    ),
    path(
        "login/",
        LoginAPIView.as_view(),
        name="api_login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "services/",
        ServiceListAPIView.as_view(),
        name="api_service_list",
    ),
    path(
        "bookings/",
        BookingCreateAPIView.as_view(),
        name="api_create_booking",
    ),
    path(
        "bookings/history/",
        BookingHistoryAPIView.as_view(),
        name="api_booking_history",
    ),
]