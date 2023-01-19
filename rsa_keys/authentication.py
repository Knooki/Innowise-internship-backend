# import jwt
# import re
# from rest_framework.authentication import BaseAuthentication
# from django.contrib.auth import get_user_model
# from rest_framework import exceptions

# from innotter.settings import (
#     ACCESS_PUBLIC,
#     INTERNAL_EXTRA_JWT_OPTIONS,
#     JWT_UNAUTHENTICATED_URL_PATTERNS,
# )


# class SafeJWTAuthentication(BaseAuthentication):
#     def authenticate(self, request):
#         User = get_user_model()
        
#         if any(
#             re.fullmatch(pattern, request.path)
#             for pattern in JWT_UNAUTHENTICATED_URL_PATTERNS
#         ):
#             return User(None), None

#         access_token = request.headers.get("authorization").split(" ")[-1]

#         options = INTERNAL_EXTRA_JWT_OPTIONS

#         payload = jwt.decode(
#             access_token, ACCESS_PUBLIC, algorithms=["RS256"], options=options
#         )

#         user = User.objects.filter(pk=payload["user_id"]).first()

#         if not user or not user.is_active:
            
#             raise exceptions.AuthenticationFailed("User not found. Deleting refresh keys.")
#             # return User(None), None
        
#         return (User(user), payload)
