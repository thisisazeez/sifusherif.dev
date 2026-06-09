"""
Management command: create_superuser_env

Creates a Django superuser from environment variables.
Idempotent — safe to run on every deploy; does nothing if the user exists.

Required env vars:
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_EMAIL
    DJANGO_SUPERUSER_PASSWORD
"""

import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create a superuser from environment variables (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email    = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(
                self.style.WARNING(
                    "[create_superuser_env] Skipped — "
                    "DJANGO_SUPERUSER_USERNAME / EMAIL / PASSWORD not set."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"[create_superuser_env] Superuser '{username}' already exists. Skipping."
                )
            )
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(
                f"[create_superuser_env] Superuser '{username}' created successfully."
            )
        )
