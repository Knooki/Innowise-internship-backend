from rest_framework.response import Response
from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import action

from accounts.models import User

from innotter.settings import (
    ACCESS_EXP_M,
    ACCESS_PRIVATE,
    ACCESS_PHRASE,
    REFRESH_PRIVATE,
    REFRESH_PHRASE,
    REFRESH_EXP_D,
)


from accounts.serializers import UserSerializer

from .utils import generate_jwt_token

from .services import JwtTokenValidation

class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="login")
    def login(self, request) -> Response:

        username = request.data.get("username")
        password = request.data.get("password")

        if (username is None) or (password is None):
            raise exceptions.NotAuthenticated("username and password required")

        user = User.objects.filter(username=username).first()
        if user is None:
            raise exceptions.AuthenticationFailed("user not found")

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("wrong password")

        access_token = generate_jwt_token(
            user.id, ACCESS_PRIVATE, ACCESS_PHRASE, 0, ACCESS_EXP_M
        )
        refresh_token = generate_jwt_token(
            user.id, REFRESH_PRIVATE, REFRESH_PHRASE, REFRESH_EXP_D, 0
        )

        return self.create_auth_response(user, refresh_token, access_token)

    @action(detail=False, methods=["GET"], name="refresh")
    def refresh(self, request) -> Response:
        refresh_token = request.COOKIES.get("refreshtoken")

        user = JwtTokenValidation(refresh_token).validate_refresh_token()

        access_token = generate_jwt_token(
            user.id, ACCESS_PRIVATE, ACCESS_PHRASE, 0, ACCESS_EXP_M
        )
        refresh_token = generate_jwt_token(
            user.id, REFRESH_PRIVATE, REFRESH_PHRASE, REFRESH_EXP_D, 0
        )

        return self.create_auth_response(user, refresh_token, access_token)

    def create_auth_response(self, user, refresh_token, access_token):
        response = Response()
        serialized_user = UserSerializer(user).data

        response.set_cookie(key="refreshtoken", value=refresh_token, httponly=True)
        response.data = {
            "access_token": access_token,
            "user": serialized_user,
            "expires_in": ACCESS_EXP_M * 60,  # in sec
            # "scope": "openid offline_access",
            # "id_token": "eyJ...0NE",
            "token_type": "Bearer",
        }

        response.status_code = status.HTTP_200_OK

        return response
