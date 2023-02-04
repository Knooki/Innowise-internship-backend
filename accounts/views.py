from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers.user_serializer import UserSerializer
from .serializers.user_registration_serializer import UserRegistrationSerializer


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
