from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import ProviderProfile, User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }
        ),
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }
        ),
    )

    mobile_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Mobile number",
            }
        ),
    )

    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Confirm password",
            }
        ),
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "mobile_number",
            "user_type",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return email

        email = email.lower().strip()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get("mobile_number")

        if not mobile_number:
            return mobile_number

        mobile_number = mobile_number.strip()

        if User.objects.filter(
            mobile_number=mobile_number
        ).exists():
            raise forms.ValidationError(
                "An account with this mobile number already exists."
            )

        return mobile_number


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile_number",
            "address",
            "profile_image",
        ]

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
            "mobile_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Mobile number",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your address",
                    "rows": 4,
                }
            ),
            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            return email

        email = email.lower().strip()

        duplicate_user = User.objects.filter(
            email__iexact=email
        ).exclude(
            pk=self.instance.pk
        )

        if duplicate_user.exists():
            raise forms.ValidationError(
                "Another account already uses this email."
            )

        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get("mobile_number")

        if not mobile_number:
            return mobile_number

        mobile_number = mobile_number.strip()

        duplicate_user = User.objects.filter(
            mobile_number=mobile_number
        ).exclude(
            pk=self.instance.pk
        )

        if duplicate_user.exists():
            raise forms.ValidationError(
                "Another account already uses this mobile number."
            )

        return mobile_number


class ProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile

        fields = [
            "business_name",
            "bio",
            "experience_years",
            "service_location",
        ]

        widgets = {
            "business_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Business or professional name",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Describe your services",
                    "rows": 5,
                }
            ),
            "experience_years": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Years of experience",
                }
            ),
            "service_location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Service location",
                }
            ),
        }


class OTPForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="OTP",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter 6-digit OTP",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
            }
        ),
    )

    def clean_otp_code(self):
        otp_code = self.cleaned_data.get(
            "otp_code",
            "",
        ).strip()

        if not otp_code.isdigit():
            raise forms.ValidationError(
                "OTP must contain only numbers."
            )

        return otp_code