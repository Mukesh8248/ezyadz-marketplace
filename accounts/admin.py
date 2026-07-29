from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone

from .models import OTPVerification, ProviderProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "mobile_number",
        "user_type",
        "is_mobile_verified",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    list_filter = (
        "user_type",
        "is_mobile_verified",
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "mobile_number",
    )

    ordering = (
        "-date_joined",
    )

    readonly_fields = (
        "last_login",
        "date_joined",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "EZYADZ Profile",
            {
                "fields": (
                    "mobile_number",
                    "user_type",
                    "address",
                    "profile_image",
                    "is_mobile_verified",
                ),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "EZYADZ Profile",
            {
                "classes": (
                    "wide",
                ),
                "fields": (
                    "email",
                    "mobile_number",
                    "user_type",
                    "first_name",
                    "last_name",
                    "is_mobile_verified",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = (
        "business_name",
        "user",
        "experience_years",
        "service_location",
        "is_approved",
        "approved_at",
        "created_at",
    )

    list_filter = (
        "is_approved",
        "created_at",
        "approved_at",
    )

    search_fields = (
        "business_name",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__mobile_number",
        "service_location",
    )

    readonly_fields = (
        "approved_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "user",
    )

    actions = (
        "approve_selected_providers",
        "reject_selected_providers",
    )

    @admin.action(
        description="Approve selected providers"
    )
    def approve_selected_providers(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            is_approved=True,
            approved_at=timezone.now(),
        )

        self.message_user(
            request,
            (
                f"{updated_count} provider account(s) "
                "approved successfully."
            ),
            level="success",
        )

    @admin.action(
        description="Reject selected providers"
    )
    def reject_selected_providers(
        self,
        request,
        queryset,
    ):
        updated_count = queryset.update(
            is_approved=False,
            approved_at=None,
        )

        self.message_user(
            request,
            (
                f"{updated_count} provider account(s) "
                "marked as not approved."
            ),
            level="warning",
        )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "otp_code",
        "is_verified",
        "created_at",
        "expires_at",
        "otp_status",
    )

    list_filter = (
        "is_verified",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__mobile_number",
        "otp_code",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    list_select_related = (
        "user",
    )

    @admin.display(
        description="Status",
    )
    def otp_status(self, obj):
        if obj.is_verified:
            return "Verified"

        if obj.expires_at and obj.expires_at <= timezone.now():
            return "Expired"

        return "Pending"