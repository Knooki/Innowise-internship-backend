from rest_framework import viewsets, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from posts.serializers.pages.page_serializers import ShortInfoPageSerializer
from posts.serializers.pages.block_page_serializer import BlockPageSerializer
from posts.services.follow_request_service import FollowRequestService
from posts.services.page_access_level_service import PageAccessLevelService
from posts.services.page_block_status_service import PageBlockStatusService
from posts.permissions import (
    ForbidAccess,
    IsFollower,
    IsAdminOrModerator,
    IsOwner,
    IsAuthenticatedUser,
)


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = ShortInfoPageSerializer

    def get_queryset(self):
        service = PageBlockStatusService(self.request)
        service.update_blockstatus_on_all_pages()
        queryset = service.get_query_set()
        return queryset

    def get_permissions(self):
        permission_classes = []
        match self.action:
            case "list" | "retrieve":
                permission_classes = []
            case "create" | "follow":
                permission_classes = [IsAuthenticatedUser]
            case "partial_update" | "follow_requests":
                permission_classes = [IsOwner]
            case "destroy":
                permission_classes = [IsOwner | IsAdminOrModerator]
            case "blocktime":
                permission_classes = [IsAdminOrModerator]
            case "unfollow":
                permission_classes = [IsFollower]
            case _:
                permission_classes = [ForbidAccess]

        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None):
        user = request.user
        page = self.get_object()
        serializer = PageAccessLevelService().get_serializer(page, user)
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
        methods=["GET", "PATCH"],
        url_path="follow_requests/?(?P<f_pk>[^/.]+)?",
    )
    def follow_requests(self, request, pk=None, f_pk=None) -> Response:
        page = self.get_object()
        service = FollowRequestService(page, f_pk)
        service.is_private_page()

        if request.method == "GET":
            data = service.get_follow_requests()
        else:
            service.confirm_subscription()
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
