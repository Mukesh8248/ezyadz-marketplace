from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path(
        "register/",
        views.register_view,
        name="register",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "verify-otp/",
        views.verify_otp_view,
        name="verify_otp",
    ),
    path(
        "dashboard/",
        views.dashboard_view,
        name="dashboard",
    ),
    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),
    path(
        "change-password/",
        views.change_password_view,
        name="change_password",
    ),
    path(
        "forgot-password/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/forgot_password.html",
        ),
        name="password_reset",
    ),
]