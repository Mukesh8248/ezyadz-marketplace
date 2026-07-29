import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the Render Django superuser."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get(
            "DJANGO_SUPERUSER_USERNAME"
        )

        email = os.environ.get(
            "DJANGO_SUPERUSER_EMAIL"
        )

        password = os.environ.get(
            "DJANGO_SUPERUSER_PASSWORD"
        )

        if not username:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USERNAME is not set."
                )
            )
            return

        if not email:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_EMAIL is not set."
                )
            )
            return

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_PASSWORD is not set."
                )
            )
            return

        user = User.objects.filter(
            username=username
        ).first()

        if user:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True

            if hasattr(user, "is_mobile_verified"):
                user.is_mobile_verified = True

            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    "Existing admin account updated successfully."
                )
            )

            return

        user_data = {
            "username": username,
            "email": email,
            "password": password,
        }

        model_fields = {
            field.name
            for field in User._meta.get_fields()
        }

        if "user_type" in model_fields:
            user_data["user_type"] = "customer"

        if "is_mobile_verified" in model_fields:
            user_data["is_mobile_verified"] = True

        User.objects.create_superuser(
            **user_data
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Render admin account created successfully."
            )
        )