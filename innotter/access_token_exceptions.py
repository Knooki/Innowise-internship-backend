from rest_framework.exceptions import APIException


class AccessTokenExpired(APIException):
    status_code = 403
    default_detail = "Authentication access token has expired. Refresh it using refresh token on /refresh"
    default_code = "Access Token Expired"


class InvalidAccessToken(APIException):
    status_code = 401
    default_detail = (
        "Access Token validation has failed. Please send valid access token."
    )
    default_code = "Access Token validation has failed"


class AccessTokenNotFound(APIException):
    status_code = 400
    default_detail = "Access Token not found. Please put it in Authorization header."
    default_code = "Access Token not found"

class NoKeywordInAuthorization(APIException):
    status_code = 400
    default_detail = "Authorization header must start with Bearer followed by its token"
    default_code = "No Keyword found in Authorization header"
