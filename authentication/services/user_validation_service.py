from rest_framework import exceptions

from accounts.models import User

MESSAGES = {
    "UserNotFound": "User in given token not found.",
    "UserIsDeactivated": "Given user is deactivated.",
    "UserIsBlocked": "Given user is blocked.",
}


def validate_user_service(user_id: int) -> User:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed(MESSAGES["UserNotFound"])

    if not user.is_active:
        raise exceptions.AuthenticationFailed(MESSAGES["UserIsDeactivated"])

    if user.is_blocked:
        raise exceptions.AuthenticationFailed(MESSAGES["UserIsBlocked"])

    return user
