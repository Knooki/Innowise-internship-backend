from rest_framework.response import Response
from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import action

from accounts.models import User

from django.conf import settings

from .services.jwt_token_generation import JwtTokenGenerationService

from .serializers.login_serializer import LoginSerializer
from .services.refresh_token_validation_service import RefreshTokenValidationService


class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="login")
    def login(self, request) -> Response:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data
        data = JwtTokenGenerationService(user_id).generate_data_for_response()
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], name="refresh")
    def refresh(self, request) -> Response:
        refresh_token_service = RefreshTokenValidationService(request)
        refresh_token_service.validate()
        user_id = refresh_token_service.get_validated_user_id()
        data = JwtTokenGenerationService(user_id).generate_data_for_response()
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["PATCH"], name="password_reset")
    def password_reset(self, request) -> Response:
        # there will be email service

        # user = AccessTokenService(request=request).validate_and_return_user()
        # serializer = PasswordResetSerializer(data=request.data, user=user)
        # serializer.is_valid(raise_exception=True)
        # serializer.update(serializer.validated_data)
        # return Response(status=status.HTTP_201_CREATED)
        pass
