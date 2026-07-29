from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "provider",
        "service",
        "booking_date",
        "status",
        "total_amount",
    )
    list_filter = (
        "status",
        "booking_date",
    )
    search_fields = (
        "customer__username",
        "provider__username",
        "service__title",
    )