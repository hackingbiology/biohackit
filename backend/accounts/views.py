# SPDX-License-Identifier: AGPL-3.0-or-later
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import MeSerializer, ProfileSerializer, RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(MeSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)


class PublicProfileView(APIView):
    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request, display_name):
        profile = get_object_or_404(
            Profile, display_name=display_name, is_public=True, user__is_public=True
        )
        return Response(ProfileSerializer(profile).data)


ERASE_CHOICES = {
    "delete_everything": {
        "available": True,
        "label": "Delete everything",
        "description": (
            "Your account, profile, lab reports, results, measurements and the "
            "original lab files we kept are permanently deleted now."
        ),
    },
    "keep_for_research": {
        "available": False,
        "label": "Keep de-identified data and reports public for research",
        "description": (
            "Delete the account but leave de-identified data and reports public "
            "for research."
        ),
        "reason": "de-identification not implemented yet",
        "consent": "analytics-and-open-data",
    },
}
CLONES_NOTICE = (
    "Copies of public data that other people have already cloned are outside "
    "this instance's control and cannot be recalled."
)


class EraseAccountView(APIView):
    """Owner-only account erasure (Q57): states the notice, then deletes everything."""

    def get(self, request):
        return Response(
            {
                "notice": CLONES_NOTICE,
                "deletes": [
                    "account and profile",
                    "lab reports and results",
                    "measurements",
                    "retained original lab files",
                ],
                "choices": ERASE_CHOICES,
            }
        )

    def post(self, request):
        choice = request.data.get("choice")
        if choice not in ERASE_CHOICES:
            return Response(
                {"detail": "choice must be delete_everything or keep_for_research."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.data.get("confirm") is not True:
            return Response(
                {"detail": "Set confirm to true to delete."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not ERASE_CHOICES[choice]["available"]:
            return Response(
                {"detail": ERASE_CHOICES[choice]["reason"]},
                status=status.HTTP_409_CONFLICT,
            )
        with transaction.atomic():
            request.user.delete()
        return Response({"notice": CLONES_NOTICE, "deleted": True})
