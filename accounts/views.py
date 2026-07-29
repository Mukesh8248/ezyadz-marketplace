import secrets
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.utils import timezone

from bookings.models import Booking
from marketplace.models import Service

from .forms import (
    OTPForm,
    ProfileForm,
    ProviderProfileForm,
    RegisterForm,
)
from .models import OTPVerification, ProviderProfile


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # Your User model uses is_mobile_verified.
            user.is_mobile_verified = False
            user.save()

            # Your User model uses user_type, not role.
            if user.user_type == "provider":
                ProviderProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "business_name": f"{user.username}'s Services"
                    },
                )

            # Create a six-digit OTP.
            otp_code = f"{secrets.randbelow(1_000_000):06d}"

            otp_record = OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=timezone.now() + timedelta(minutes=10),
            )

            # Mock OTP shown in the VS Code terminal.
            print(
                f"EZYADZ OTP for {user.email}: "
                f"{otp_record.otp_code}"
            )

            request.session["verification_user_id"] = user.id

            messages.success(
                request,
                "Registration successful. "
                "Check the terminal for your mock OTP.",
            )
            return redirect("verify_otp")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form},
    )


def verify_otp_view(request):
    user_id = request.session.get("verification_user_id")

    if not user_id:
        messages.error(
            request,
            "Verification session expired. Please register again.",
        )
        return redirect("register")

    otp_record = (
        OTPVerification.objects
        .filter(
            user_id=user_id,
            is_verified=False,
        )
        .order_by("-created_at")
        .first()
    )

    if request.method == "POST":
        form = OTPForm(request.POST)

        if form.is_valid():
            # Make sure your OTPForm field is named "otp".
            entered_otp = form.cleaned_data["otp"]

            if otp_record is None:
                messages.error(
                    request,
                    "OTP was not found. Please register again.",
                )

            elif otp_record.is_expired():
                messages.error(
                    request,
                    "OTP has expired. Please register again.",
                )

            elif otp_record.otp_code != entered_otp:
                messages.error(
                    request,
                    "Invalid OTP. Please try again.",
                )

            else:
                user = otp_record.user
                user.is_mobile_verified = True
                user.save(update_fields=["is_mobile_verified"])

                otp_record.is_verified = True
                otp_record.save(update_fields=["is_verified"])

                request.session.pop(
                    "verification_user_id",
                    None,
                )

                messages.success(
                    request,
                    "Account verified successfully. You can now log in.",
                )
                return redirect("login")

    else:
        form = OTPForm()

    return render(
        request,
        "accounts/verify_otp.html",
        {"form": form},
    )


@login_required
def dashboard_view(request):
    # Use user_type instead of role.
    if request.user.user_type == "provider":
        services = Service.objects.filter(
            provider=request.user
        )

        bookings = Booking.objects.filter(
            provider=request.user
        ).order_by("-id")

        return render(
            request,
            "dashboard/provider_dashboard.html",
            {
                "services": services,
                "bookings": bookings[:5],
                "booking_count": bookings.count(),
            },
        )

    bookings = Booking.objects.filter(
        customer=request.user
    ).order_by("-id")

    return render(
        request,
        "dashboard/customer_dashboard.html",
        {
            "bookings": bookings[:5],
            "booking_count": bookings.count(),
        },
    )


@login_required
def profile_view(request):
    user_form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    provider_form = None

    # Use user_type instead of role.
    if request.user.user_type == "provider":
        profile, created = ProviderProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "business_name": (
                    f"{request.user.username}'s Services"
                )
            },
        )

        provider_form = ProviderProfileForm(
            request.POST or None,
            instance=profile,
        )

    if request.method == "POST":
        user_valid = user_form.is_valid()

        provider_valid = (
            provider_form.is_valid()
            if provider_form is not None
            else True
        )

        if user_valid and provider_valid:
            user_form.save()

            if provider_form is not None:
                provider_form.save()

            messages.success(
                request,
                "Profile updated successfully.",
            )
            return redirect("profile")

    return render(
        request,
        "accounts/profile.html",
        {
            "user_form": user_form,
            "provider_form": provider_form,
        },
    )


@login_required
def change_password_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(
            user=request.user,
            data=request.POST,
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Password changed successfully.",
            )
            return redirect("profile")

    else:
        form = PasswordChangeForm(
            user=request.user
        )

    return render(
        request,
        "accounts/change_password.html",
        {"form": form},
    )