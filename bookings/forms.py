from django import forms
from django.utils import timezone

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "booking_date",
            "booking_time",
            "address",
            "customer_notes",
        ]
        widgets = {
            "booking_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "min": timezone.localdate().isoformat(),
                }
            ),
            "booking_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "address": forms.Textarea(
                attrs={"rows": 3}
            ),
            "customer_notes": forms.Textarea(
                attrs={"rows": 3}
            ),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data["booking_date"]

        if booking_date < timezone.localdate():
            raise forms.ValidationError(
                "Booking date cannot be in the past."
            )

        return booking_date