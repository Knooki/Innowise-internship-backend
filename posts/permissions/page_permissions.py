from rest_framework import permissions

from posts.models import Page


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("list", "retrieve"):
            return request.user
        return False


class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("destroy", "blocktime"):
            user = request.user
            return user and user.role in ("admin", "moderator")
        return False


class IsAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("create", "follow"):
            user = request.user
            return user and user.role == "user"
        return False


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ("partial_update", "follow_requests", "destroy"):
            user = request.user
            page_id = view.kwargs.get("pk", None)
            page = Page.objects.get(pk=page_id)
            return user and page.owner == user
        return False


class IsFollower(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "unfollow":
            user = request.user
            return user and user.role == "user"
        return False

    def has_object_permission(self, request, view, obj):
        if view.action == "unfollow":
            user = request.user
            return user in obj.followers.all()
        return False
