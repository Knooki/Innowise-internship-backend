<<<<<<< HEAD
=======
import jwt
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)
import datetime

from rest_framework.response import Response
from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import action

from django.contrib.auth import get_user_model

from innotter.settings import (
<<<<<<< HEAD
=======
    INTERNAL_EXTRA_JWT_OPTIONS,
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)
    ACCESS_EXP_M,
    ACCESS_PRIVATE,
    ACCESS_PHRASE,
    REFRESH_PRIVATE,
    REFRESH_PHRASE,
    REFRESH_EXP_D,
)


from accounts.serializers import UserSerializer
<<<<<<< HEAD
from .utils import (
    generate_jwt_token,
    decode_refresh_token,
    update_valid_refresh_tokens_to_invalid,
)
=======
from .utils import generate_jwt_token, decode_refresh_token
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)
from .models import UserToken


class AuthenticationView(viewsets.ViewSet):
    @action(detail=False, methods=["POST"], name="login")
    def login(self, request) -> Response:

        User = get_user_model()
        username = request.data.get("username")
        password = request.data.get("password")

        if (username is None) or (password is None):
            raise exceptions.NotAuthenticated("username and password required")

        user = User.objects.filter(username=username).first()
        if user is None:
            raise exceptions.AuthenticationFailed("user not found")

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed("wrong password")

<<<<<<< HEAD
        update_valid_refresh_tokens_to_invalid(user.id)
=======
        # Update all tokens, that are valid to invalid
        user_tokens = UserToken.objects.filter(user_id=user.id).filter(is_valid=True)
        for object in user_tokens:
            object.is_valid = False

        UserToken.objects.bulk_update(user_tokens, ["is_valid"])
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)

        access_token = generate_jwt_token(
            user.id, ACCESS_PRIVATE, ACCESS_PHRASE, 0, ACCESS_EXP_M
        )
        refresh_token = generate_jwt_token(
            user.id, REFRESH_PRIVATE, REFRESH_PHRASE, REFRESH_EXP_D, 0
        )

<<<<<<< HEAD
        return self.create_auth_response(user, refresh_token, access_token)
=======
        return self.create_response(user, refresh_token, access_token)
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)

    @action(detail=False, methods=["GET"], name="refresh")
    def refresh(self, request) -> Response:
        User = get_user_model()

        refresh_token = request.COOKIES.get("refreshtoken")

        payload = decode_refresh_token(refresh_token)

        # If user doesn't exist in database
        user = User.objects.filter(id=payload["user_id"]).first()
        if user is None:
            raise exceptions.AuthenticationFailed(
                "User in refresh key not found. Please sign in again."
            )

        # If refresh_token doesn't exist in database
<<<<<<< HEAD
        user_token = UserToken.objects.filter(refresh_token=refresh_token)
=======
        user_token = UserToken.objects.filter(refresh_token=refresh_token).get()
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)
        if not user_token:
            UserToken.objects.filter(user_id=payload["user_id"]).delete()
            raise exceptions.AuthenticationFailed(
                "The Refresh Token is invalid. Please sign in again."
            )
<<<<<<< HEAD

        user_token = user_token.first()
=======
            
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)
        # If refresh_token is old
        if not user_token.is_valid:
            UserToken.objects.filter(user_id=payload["user_id"]).delete()
            raise exceptions.AuthenticationFailed(
                "The refresh token is invalid, all refresh tokens of this user are deleted. Sign in again."
            )

        user_token.is_valid = False
        user_token.save()

        access_token = generate_jwt_token(
            user.id, ACCESS_PRIVATE, ACCESS_PHRASE, 0, ACCESS_EXP_M
        )
        refresh_token = generate_jwt_token(
            user.id, REFRESH_PRIVATE, REFRESH_PHRASE, REFRESH_EXP_D, 0
        )

<<<<<<< HEAD
        return self.create_auth_response(user, refresh_token, access_token)

    def create_auth_response(self, user, refresh_token, access_token):
=======
        return self.create_response(user, refresh_token, access_token)

    def create_response(self, user, refresh_token, access_token):
>>>>>>> 13bf44d (iib-4/added-cryptograpy-pytest-django-django-csp-packages-refactored-settings.py)
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
