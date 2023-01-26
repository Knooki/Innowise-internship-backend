import jwt
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework import viewsets, status
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PasswordResetUserSerializer,
)
from rest_framework.response import Response

from innotter.settings import ACCESS_PUBLIC
from authentication.services import JwtTokenValidation


class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=["POST"], name="registration")
    def registration(self, request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=False, methods=["PATCH"], name="password_reset")
    def password_reset(self, request) -> Response:

        access_token = request.headers.get("Authorization").split(" ")[-1]
        user = JwtTokenValidation(access_token).validate_access_token()
        serializer = PasswordResetUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)
        return Response(status=status.HTTP_201_CREATED)
