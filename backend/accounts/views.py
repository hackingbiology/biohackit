# SPDX-License-Identifier: AGPL-3.0-or-later
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
