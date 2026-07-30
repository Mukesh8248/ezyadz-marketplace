from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import ProviderProfile, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your email",
                "autocomplete": "email",
            }
        ),
    )

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
                "autocomplete": "username",
            }
        ),
    )

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
                "autocomplete": "new-password",
            }
        ),
    )

    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "user_type",
            "password1",
            "password2",
        )

        widgets = {
            "user_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get(
            "email",
            "",
        ).strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter username",
                "autocomplete": "username",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter password",
                "autocomplete": "current-password",
            }
        ),
    )


class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(
        label="Enter OTP",
        required=True,
        min_length=6,
        max_length=6,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "class": "otp-input",
                "placeholder": "Enter 6-digit OTP",
                "inputmode": "numeric",
                "pattern": "[0-9]{6}",
                "maxlength": "6",
                "minlength": "6",
                "autocomplete": "one-time-code",
                "autofocus": True,
            }
        ),
    )

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get(
            "otp_code",
            "",
        ).strip()

        if not otp_code:
            raise forms.ValidationError(
                "Please enter the OTP."
            )

        if not otp_code.isdigit():
            raise forms.ValidationError(
                "OTP must contain only numbers."
            )

        if len(otp_code) != 6:
            raise forms.ValidationError(
                "OTP must be exactly 6 digits."
            )

        return otp_code


# Alias so old views importing OTPForm continue to work.
OTPForm = OTPVerificationForm


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Last name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Email address",
                }
            ),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "address",
            "profile_image",
        )

        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "mobile_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),
        }


class ProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = (
            "business_name",
            "bio",
            "experience_years",
            "service_location",
        )

        widgets = {
            "business_name": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "experience_years": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "service_location": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Current password",
            }
        )
    )

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "New password",
            }
        )
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm new password",
            }
        )
    )