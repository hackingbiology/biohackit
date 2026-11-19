# SPDX-License-Identifier: AGPL-3.0-or-later
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Profile, SocialHandle, User


class SocialHandleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialHandle
        fields = ["platform", "handle", "url"]


class ProfileSerializer(serializers.ModelSerializer):
    social_handles = SocialHandleSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "display_name",
            "date_of_birth",
            "sex",
            "ethnicity",
            "height_cm",
            "is_public",
            "social_handles",
        ]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    display_name = serializers.SlugField(max_length=50, required=False)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email exists.")
        return value

    def validate_display_name(self, value):
        if Profile.objects.filter(display_name=value).exists():
            raise serializers.ValidationError("This display name is taken.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    @transaction.atomic
    def create(self, data):
        user = User.objects.create_user(data["email"], data["password"])
        name = data.get("display_name") or f"user-{user.pk}"
        Profile.objects.create(user=user, display_name=name)
        return user


class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "is_public", "profile"]
