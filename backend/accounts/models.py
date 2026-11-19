# SPDX-License-Identifier: AGPL-3.0-or-later
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra["is_staff"] = True
        extra["is_superuser"] = True
        return self._create(email, password, **extra)


class User(AbstractUser):
    """Email-primary account; no username. Public by default."""

    username = None
    email = models.EmailField(unique=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []
    objects = UserManager()

    def __str__(self):
        return self.email


class Sex(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    INTERSEX = "I", "Intersex"
    OTHER = "X", "Other"
    PREFER_NOT = "N", "Prefer not to say"


class Profile(models.Model):
    """Public-by-default profile; `display_name` is the public slug (Q2)."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    display_name = models.SlugField(max_length=50, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=Sex.choices, blank=True)
    ethnicity = models.CharField(max_length=100, null=True, blank=True)
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name


class SocialHandle(models.Model):
    class Platform(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        WECHAT = "wechat", "WeChat"
        XIAOHONGSHU = "xiaohongshu", "Xiaohongshu (RED)"
        RAPAMYCIN_NEWS = "rapamycin_news", "Rapamycin News"
        OTHER = "other", "Other"

    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="social_handles"
    )
    platform = models.CharField(max_length=20, choices=Platform.choices)
    handle = models.CharField(max_length=100)
    url = models.URLField(blank=True)
