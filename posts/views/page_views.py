from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from posts.serializers.pages.page_serializers import (
    ShortInfoPageSerializer,
    FullAccessPageSerializer,
)
from posts.serializers.pages.block_page_serializer import BlockPageSerializer
from posts.services.follow_request_service import FollowRequestService
from posts.services.page_access_level_service import PageAccessLevelService
from posts.services.page_block_status_service import PageBlockStatusService
from posts.permissions import (
    ReadOnly,
    IsFollower,
    IsAdminOrModerator,
    IsOwner,
    IsAuthenticatedUser,
)


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = ShortInfoPageSerializer
    permission_classes = [
        ReadOnly | IsFollower | IsAdminOrModerator | IsOwner | IsAuthenticatedUser
    ]

    def get_queryset(self):
        service = PageBlockStatusService(self.request)
        service.update_blockstatus_on_all_pages()
        queryset = service.get_query_set()
        return queryset

    def partial_update(self, request, pk=None):
        # Here we customize a serializer for our patch method
        page = self.get_object()
        serializer = FullAccessPageSerializer(instance=page, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        serializer.save()

        return Response(serializer.data)

    def create(self, request):
        # little customization of create method
        # adding to owner of the page current user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = request.user
        page = self.get_object()
        service = PageAccessLevelService()
        serializer = service.get_serializer(page=page, user=user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["PATCH"],
        name="blocktime",
    )
    def blocktime(self, request, pk=None) -> Response:
        page = self.get_object()
        serializer = BlockPageSerializer(data=request.data, instance=page)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["PATCH"],
        url_path="follow_requests/?(?P<f_pk>[^/.]+)?",
    )
    def follow_requests(self, request, pk=None, f_pk=None) -> Response:
        is_confirmed = request.query_params.get("is_confirmed")
        page = self.get_object()
        service = FollowRequestService(page, f_pk, is_confirmed)
        service.validate()
        service.is_private_page()
        service.update_follow_requests()
        data = page.follow_requests.values()
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], name="follow")
    def follow(self, request, pk=None):
        page = self.get_object()
        FollowRequestService(page=page).validate_and_add_follow_request(request)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["PATCH"], name="unfollow")
    def unfollow(self, request, pk=None):
        page = self.get_object()
        user = request.user
        page.followers.remove(user)
        return Response(status=status.HTTP_200_OK)
