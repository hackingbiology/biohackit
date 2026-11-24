# SPDX-License-Identifier: AGPL-3.0-or-later
"""Idempotent staging seed: one demo account and nothing else.

DEMO_USERNAME is used as the account's sign-in e-mail address (the user model
has no username). No measurements, ranges, doses or other health values are
created here; see docs/QUESTIONS.md (staging demo data).
"""

import os
from typing import Any

from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Create the demo account from DEMO_USERNAME / DEMO_PASSWORD (idempotent)."

    def handle(self, *args: Any, **options: Any) -> None:
        email = os.environ.get("DEMO_USERNAME", "")
        password = os.environ.get("DEMO_PASSWORD", "")
        if not (email and password):
            self.stdout.write("seed_demo: DEMO_USERNAME/DEMO_PASSWORD unset, skipping")
            return
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.create_user(email=email, password=password)
            self.stdout.write("seed_demo: demo user created")
        else:
            self.stdout.write("seed_demo: demo user exists")
        # Mandatory e-mail verification would otherwise block sign-in.
        EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={"verified": True, "primary": True},
        )
