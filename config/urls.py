from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from marketplace.views import home_view

urlpatterns = [
    # Admin
    path(
        "admin/",
        admin.site.urls,
    ),

    # Home
    path(
        "",
        home_view,
        name="home",
    ),

    # Accounts
    path(
        "accounts/",
        include("accounts.urls"),
    ),

    # Marketplace Services
    path(
        "services/",
        include("marketplace.urls"),
    ),

    # Bookings
    path(
        "bookings/",
        include("bookings.urls"),
    ),

    # Wallet
    path(
        "wallets/",
        include("wallets.urls"),
    ),

    # REST API
    path(
        "api/",
        include("api.urls"),
    ),
]

# ==========================================================
# Serve uploaded media files during development
# ==========================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

# ==========================================================
# Serve static files during development
# (WhiteNoise serves static files in production)
# ==========================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )