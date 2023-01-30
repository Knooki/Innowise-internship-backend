from rest_framework import serializers

from authentication.models import UserToken

from accounts.models import User


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=1000)

    def validate(self, data):
        refresh_token = data.get("refresh_token")
        user_token = UserToken.objects.filter(refresh_token=refresh_token).first()
        if not user_token:
            msg = {"refresh_token": "such refresh token not found"}
            raise serializers.ValidationError(msg, code="authorization")
        if not user_token.is_valid:
            msg = {
                "refresh_token": "this refresh token is old. All refresh tokens of this user deleted. Please login again"
            }
            UserToken.objects.filter(user_id=user_token.user_id).delete()
            raise serializers.ValidationError(msg, code="authorization")
        user = User.objects.filter(id=user_token.user_id).first()
        if not user:
            msg = {"refresh_token": "User in this refresh token doesn't exist anymore."}
            UserToken.objects.filter(user_id=user_token.user_id).delete()
            raise serializers.ValidationError(msg, code="authorization")
        return user_token.user_id
