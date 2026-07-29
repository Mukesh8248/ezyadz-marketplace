from django.contrib import admin

from .models import (
    Category,
    ProviderAvailability,
    Service,
    ServiceImage,
)


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "provider",
        "category",
        "price",
        "is_available",
    )

    list_filter = (
        "category",
        "is_available",
    )

    search_fields = (
        "title",
        "provider__username",
        "category__name",
    )

    list_per_page = 20

    inlines = [
        ServiceImageInline,
    ]


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service",
    )

    search_fields = (
        "service__title",
    )


@admin.register(ProviderAvailability)
class ProviderAvailabilityAdmin(admin.ModelAdmin):
    pass