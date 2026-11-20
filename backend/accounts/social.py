# SPDX-License-Identifier: AGPL-3.0-or-later
"""Glue between django-allauth sign-ins and our Profile / SocialHandle models."""

from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.utils.text import slugify

from .models import Profile, SocialHandle


def ensure_profile(user, hint: str = "") -> Profile:
    existing = Profile.objects.filter(user=user).first()
    if existing:
        return existing
    base = slugify(hint or user.email.split("@")[0])[:40] or f"user-{user.pk}"
    name, n = base, 1
    while Profile.objects.filter(display_name=name).exists():
        n += 1
        name = f"{base}-{n}"
    return Profile.objects.create(user=user, display_name=name)


def sync_social_handle(user, account) -> None:
    profile = ensure_profile(user, account.extra_data.get("username", ""))
    if account.provider != "discourse_connect":
        return
    extra = account.extra_data
    username = extra.get("username")
    if not username:
        return
    base = extra.get("_base_url", "").rstrip("/")
    SocialHandle.objects.update_or_create(
        profile=profile,
        platform=SocialHandle.Platform.RAPAMYCIN_NEWS,
        defaults={"handle": username, "url": f"{base}/u/{username}" if base else ""},
    )


def _on_signed_up(request, user, sociallogin=None, **kwargs):
    if sociallogin is not None:
        sync_social_handle(user, sociallogin.account)
    else:
        ensure_profile(user)


def _on_social(request, sociallogin, **kwargs):
    sync_social_handle(sociallogin.user, sociallogin.account)


def connect() -> None:
    user_signed_up.connect(_on_signed_up, dispatch_uid="accounts_signed_up")
    social_account_added.connect(_on_social, dispatch_uid="accounts_social_added")
    social_account_updated.connect(_on_social, dispatch_uid="accounts_social_updated")
