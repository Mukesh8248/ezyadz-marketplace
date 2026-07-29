from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from bookings.models import Booking
from marketplace.models import Service

from .serializers import (
    BookingCreateSerializer,
    BookingHistorySerializer,
    LoginSerializer,
    RegisterSerializer,
    ServiceSerializer,
)


class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


class ServiceListAPIView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = (
            Service.objects
            .filter(
                is_active=True,
                is_available=True,
                provider__provider_profile__is_approved=True,
            )
            .select_related(
                "provider",
                "category",
            )
            .prefetch_related("images")
        )

        keyword = self.request.query_params.get(
            "q",
            "",
        ).strip()

        category = self.request.query_params.get(
            "category",
            "",
        ).strip()

        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(location__icontains=keyword)
            )

        if category:
            queryset = queryset.filter(
                category_id=category
            )

        return queryset


class BookingCreateAPIView(generics.CreateAPIView):
    serializer_class = BookingCreateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.CUSTOMER:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only customers can create bookings."
            )

        serializer.save()


class BookingHistoryAPIView(generics.ListAPIView):
    serializer_class = BookingHistorySerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.Role.PROVIDER:
            return Booking.objects.filter(
                provider=user
            ).select_related(
                "service",
                "customer",
                "provider",
            )

        return Booking.objects.filter(
            customer=user
        ).select_related(
            "service",
            "customer",
            "provider",
        )