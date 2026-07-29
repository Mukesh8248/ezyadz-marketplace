from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("provider", "Service Provider"),
    )

    email = models.EmailField(unique=True)

    mobile_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="customer",
    )

    address = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
    )

    is_mobile_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    @property
    def is_provider(self):
        return self.user_type == "provider"

    @property
    def is_customer(self):
        return self.user_type == "customer"


class ProviderProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="provider_profile",
    )

    business_name = models.CharField(
        max_length=150,
        blank=True,
    )

    bio = models.TextField(
        blank=True,
    )

    experience_years = models.PositiveIntegerField(
        default=0,
    )

    service_location = models.CharField(
        max_length=255,
        blank=True,
    )

    is_approved = models.BooleanField(
        default=False,
    )

    approved_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def approve(self):
        self.is_approved = True
        self.approved_at = timezone.now()

        self.save(
            update_fields=[
                "is_approved",
                "approved_at",
            ]
        )

    def __str__(self):
        if self.business_name:
            return self.business_name

        return self.user.username


class OTPVerification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_verifications",
    )

    otp_code = models.CharField(
        max_length=6,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.otp_code}"

    def is_expired(self):
        if self.expires_at is None:
            return False

        return timezone.now() > self.expires_at