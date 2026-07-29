from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from marketplace.views import home_view


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    path(
        "",
        home_view,
        name="home",
    ),

    path(
        "accounts/",
        include("accounts.urls"),
    ),

    path(
        "services/",
        include("marketplace.urls"),
    ),

    path(
        "bookings/",
        include("bookings.urls"),
    ),

    path(
        "wallets/",
        include("wallets.urls"),
    ),

    path(
        "api/",
        include("api.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )