from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    # Register
    path(
        "register/",
        views.register_view,
        name="register",
    ),

    # Login
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),

    # Logout
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    # OTP
    path(
        "verify-otp/",
        views.verify_otp_view,
        name="verify_otp",
    ),

    path(
        "resend-otp/",
        views.resend_otp_view,
        name="resend_otp",
    ),

    # Dashboard
    path(
        "dashboard/",
        views.dashboard_view,
        name="dashboard",
    ),

    # Profile
    path(
        "profile/",
        views.profile_view,
        name="profile",
    ),

    # Change Password
    path(
        "change-password/",
        views.change_password_view,
        name="change_password",
    ),
]