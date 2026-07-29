from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ProviderProfile, User
from bookings.models import Booking
from marketplace.models import Category, Service, ServiceImage


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )
    password_confirm = serializers.CharField(
        write_only=True,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "mobile_number",
            "role",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": (
                        "Passwords do not match."
                    )
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        if user.role == User.Role.PROVIDER:
            ProviderProfile.objects.create(
                user=user,
                business_name=f"{user.username}'s Services",
            )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError(
                "Invalid username or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
        ]


class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = [
            "id",
            "image",
            "is_primary",
        ]


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    provider_name = serializers.CharField(
        source="provider.username",
        read_only=True,
    )
    images = ServiceImageSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Service
        fields = [
            "id",
            "provider_name",
            "category",
            "title",
            "description",
            "price",
            "location",
            "duration_minutes",
            "is_available",
            "images",
            "created_at",
        ]


class BookingCreateSerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(
        source="service",
        queryset=Service.objects.filter(
            is_active=True,
            is_available=True,
        ),
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "service_id",
            "booking_date",
            "booking_time",
            "address",
            "customer_notes",
            "status",
            "total_amount",
            "created_at",
        ]
        read_only_fields = [
            "status",
            "total_amount",
            "created_at",
        ]

    def create(self, validated_data):
        customer = self.context["request"].user
        service = validated_data["service"]

        return Booking.objects.create(
            customer=customer,
            provider=service.provider,
            total_amount=service.price,
            **validated_data,
        )


class BookingHistorySerializer(serializers.ModelSerializer):
    service_title = serializers.CharField(
        source="service.title",
        read_only=True,
    )
    customer_name = serializers.CharField(
        source="customer.username",
        read_only=True,
    )
    provider_name = serializers.CharField(
        source="provider.username",
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = [
            "id",
            "service_title",
            "customer_name",
            "provider_name",
            "booking_date",
            "booking_time",
            "address",
            "total_amount",
            "status",
            "created_at",
        ]