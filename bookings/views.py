from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from marketplace.models import Service
from wallets.models import Commission, WalletTransaction

from .forms import BookingForm
from .models import Booking


@login_required
def create_booking_view(request, service_id):
    # Your User model uses user_type, not role.
    if request.user.user_type != "customer":
        return HttpResponseForbidden(
            "Only customers can book services."
        )

    service = get_object_or_404(
        Service,
        id=service_id,
        is_active=True,
        is_available=True,
    )

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.provider = service.provider
            booking.service = service
            booking.total_amount = service.price
            booking.save()

            messages.success(
                request,
                "Booking created successfully.",
            )
            return redirect("booking_history")
    else:
        form = BookingForm()

    return render(
        request,
        "bookings/create_booking.html",
        {
            "form": form,
            "service": service,
        },
    )


@login_required
def booking_history_view(request):
    # Your User model uses user_type, not role.
    if request.user.user_type == "provider":
        bookings = (
            Booking.objects
            .filter(provider=request.user)
            .select_related(
                "customer",
                "service",
            )
            .order_by("-created_at")
        )
    else:
        bookings = (
            Booking.objects
            .filter(customer=request.user)
            .select_related(
                "provider",
                "service",
            )
            .order_by("-created_at")
        )

    return render(
        request,
        "bookings/booking_history.html",
        {"bookings": bookings},
    )


@login_required
def update_booking_status_view(request, pk, status):
    # Prevent customers from updating booking status.
    if request.user.user_type != "provider":
        return HttpResponseForbidden(
            "Only providers can update booking status."
        )

    booking = get_object_or_404(
        Booking,
        pk=pk,
        provider=request.user,
    )

    allowed_statuses = {
        Booking.Status.ACCEPTED,
        Booking.Status.COMPLETED,
        Booking.Status.CANCELLED,
    }

    if status not in allowed_statuses:
        messages.error(
            request,
            "Invalid booking status.",
        )
        return redirect("booking_history")

    if request.method != "POST":
        return HttpResponseForbidden(
            "Status updates require POST."
        )

    if (
        booking.status == Booking.Status.COMPLETED
        and status == Booking.Status.COMPLETED
    ):
        messages.info(
            request,
            "Booking is already completed.",
        )
        return redirect("booking_history")

    with transaction.atomic():
        booking.status = status
        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        if status == Booking.Status.COMPLETED:
            process_completed_booking(booking)

    messages.success(
        request,
        (
            "Booking status changed to "
            f"{booking.get_status_display()}."
        ),
    )
    return redirect("booking_history")


def process_completed_booking(booking):
    # Avoid adding payment twice.
    if hasattr(booking, "commission"):
        return

    commission_percentage = Decimal("10.00")

    commission_amount = (
        booking.total_amount
        * commission_percentage
        / Decimal("100.00")
    )

    provider_amount = (
        booking.total_amount - commission_amount
    )

    provider_wallet = booking.provider.wallet

    provider_wallet.balance += provider_amount
    provider_wallet.save(
        update_fields=[
            "balance",
            "updated_at",
        ]
    )

    WalletTransaction.objects.create(
        wallet=provider_wallet,
        booking=booking,
        transaction_type=(
            WalletTransaction.TransactionType.CREDIT
        ),
        amount=provider_amount,
        description=(
            f"Payment received for booking #{booking.pk}"
        ),
    )

    WalletTransaction.objects.create(
        wallet=provider_wallet,
        booking=booking,
        transaction_type=(
            WalletTransaction.TransactionType.COMMISSION
        ),
        amount=commission_amount,
        description=(
            f"10% EZYADZ commission for booking #{booking.pk}"
        ),
    )

    Commission.objects.create(
        booking=booking,
        provider=booking.provider,
        booking_amount=booking.total_amount,
        commission_percentage=commission_percentage,
        commission_amount=commission_amount,
        provider_amount=provider_amount,
    )