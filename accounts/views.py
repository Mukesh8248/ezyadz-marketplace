import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.utils import timezone

from bookings.models import Booking
from marketplace.models import Service

from .forms import (
    OTPVerificationForm,
    ProfileForm,
    ProviderProfileForm,
    RegisterForm,
)
from .models import OTPVerification, ProviderProfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def dashboard_view(request):
    return render(request, "accounts/dashboard.html")
# =========================================================
# REGISTER
# =========================================================

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # User must enter the correct OTP before verification.
            user.is_mobile_verified = False
            user.save()

            # Automatically create a provider profile.
            if user.user_type == "provider":
                ProviderProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "business_name": (
                            f"{user.username}'s Services"
                        )
                    },
                )

            # Delete any old OTP records for this user.
            OTPVerification.objects.filter(
                user=user
            ).delete()

            # Generate a secure six-digit mock OTP.
            otp_code = (
                f"{secrets.randbelow(1_000_000):06d}"
            )

            otp_record = OTPVerification.objects.create(
                user=user,
                otp_code=otp_code,
                expires_at=(
                    timezone.now()
                    + timedelta(minutes=10)
                ),
                is_verified=False,
            )

            # Display OTP in the local terminal and Render logs.
            print(
                f"EZYADZ OTP for {user.email}: "
                f"{otp_record.otp_code}"
            )

            # Save the user ID temporarily in the session.
            request.session[
                "verification_user_id"
            ] = user.id

            request.session.modified = True

            messages.success(
                request,
                "Registration successful. "
                "Enter the mock OTP shown below.",
            )

            return redirect("verify_otp")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form,
        },
    )


# =========================================================
# VERIFY OTP
# =========================================================

def verify_otp_view(request):
    user_id = request.session.get(
        "verification_user_id"
    )

    if not user_id:
        messages.error(
            request,
            "Your verification session expired. "
            "Please register again.",
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

    if otp_record is None:
        request.session.pop(
            "verification_user_id",
            None,
        )

        messages.error(
            request,
            "OTP was not found. Please register again.",
        )

        return redirect("register")

    # Display mock OTP when SHOW_MOCK_OTP=True.
    mock_otp = None

    if getattr(settings, "SHOW_MOCK_OTP", False):
        mock_otp = otp_record.otp_code

    if request.method == "POST":
        form = OTPVerificationForm(
            request.POST
        )

        if form.is_valid():
            entered_otp = str(
                form.cleaned_data.get(
                    "otp_code",
                    "",
                )
            ).strip()

            # Empty OTP must never verify the account.
            if not entered_otp:
                messages.error(
                    request,
                    "Please enter the 6-digit OTP.",
                )

            # OTP must contain only numbers.
            elif not entered_otp.isdigit():
                messages.error(
                    request,
                    "OTP must contain only numbers.",
                )

            # OTP must contain exactly six digits.
            elif len(entered_otp) != 6:
                messages.error(
                    request,
                    "OTP must be exactly 6 digits.",
                )

            # Reject an expired OTP.
            elif otp_record.is_expired():
                messages.error(
                    request,
                    "OTP has expired. "
                    "Please generate a new OTP.",
                )

            # Strictly compare the submitted OTP.
            elif (
                str(otp_record.otp_code).strip()
                != entered_otp
            ):
                messages.error(
                    request,
                    "Invalid OTP. "
                    "Please enter the correct OTP.",
                )

            else:
                user = otp_record.user

                # Verify user only after correct OTP.
                user.is_mobile_verified = True
                user.save(
                    update_fields=[
                        "is_mobile_verified",
                    ]
                )

                # Mark this OTP as verified.
                otp_record.is_verified = True
                otp_record.save(
                    update_fields=[
                        "is_verified",
                    ]
                )

                # Remove verification session data.
                request.session.pop(
                    "verification_user_id",
                    None,
                )

                messages.success(
                    request,
                    "Account verified successfully. "
                    "You can now log in.",
                )

                return redirect("login")

        else:
            messages.error(
                request,
                "Please enter a valid 6-digit OTP.",
            )

    else:
        form = OTPVerificationForm()

    return render(
        request,
        "accounts/verify_otp.html",
        {
            "form": form,
            "mock_otp": mock_otp,
            "otp_expires_at": (
                otp_record.expires_at
            ),
        },
    )


# =========================================================
# RESEND OTP
# =========================================================

def resend_otp_view(request):
    user_id = request.session.get(
        "verification_user_id"
    )

    if not user_id:
        messages.error(
            request,
            "Your verification session expired. "
            "Please register again.",
        )

        return redirect("register")

    old_otp_record = (
        OTPVerification.objects
        .filter(user_id=user_id)
        .order_by("-created_at")
        .first()
    )

    if old_otp_record is None:
        messages.error(
            request,
            "User verification information was not found. "
            "Please register again.",
        )

        return redirect("register")

    user = old_otp_record.user

    # Remove all previous OTP records.
    OTPVerification.objects.filter(
        user=user
    ).delete()

    # Generate a new six-digit OTP.
    new_otp_code = (
        f"{secrets.randbelow(1_000_000):06d}"
    )

    new_otp_record = OTPVerification.objects.create(
        user=user,
        otp_code=new_otp_code,
        expires_at=(
            timezone.now()
            + timedelta(minutes=10)
        ),
        is_verified=False,
    )

    print(
        f"New EZYADZ OTP for {user.email}: "
        f"{new_otp_record.otp_code}"
    )

    messages.success(
        request,
        "A new mock OTP has been generated.",
    )

    return redirect("verify_otp")


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard_view(request):
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


# =========================================================
# PROFILE
# =========================================================

@login_required
def profile_view(request):
    user_form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )

    provider_form = None

    if request.user.user_type == "provider":
        profile, created = (
            ProviderProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    "business_name": (
                        f"{request.user.username}'s "
                        "Services"
                    )
                },
            )
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


# =========================================================
# CHANGE PASSWORD
# =========================================================

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
        {
            "form": form,
        },
    )