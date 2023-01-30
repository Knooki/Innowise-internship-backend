from rest_framework.exceptions import APIException
from rest_framework import status


class AccessTokenExpired(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Authentication access token has expired. Refresh it using refresh token on /refresh"
    default_code = "Access Token expired"


class InvalidAccessToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = (
        "Access Token validation has failed. Please send valid access token."
    )
    default_code = "Invalid Access Token"


class AccessTokenNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Access Token not found. Please put it in Authorization header."
    default_code = "Access Token not found"


class BearerKeywordNotFound(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Authorization header must start with Bearer followed by its token"
    default_code = "No Keyword found in Authorization header"


class RefreshTokenExpired(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Authentication refresh token has expired. Sign in again."
    default_code = "Refresh Token expired"


class InvalidRefreshToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = (
        "Refresh Token validation has failed. Please send valid refresh token"
    )
    default_code = "Invalid Refresh Token"


class RefreshTokenNotFound(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = (
        "Refresh Token not found. Please put it in Cookie named 'refreshtoken'"
    )
    default_code = "Refresh Token not found"
