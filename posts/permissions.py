from rest_framework import permissions

# POST(create), GET(all)
# DELETE, PUT(update), PATCH(partitial update)


class ForbidAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        return False


class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        is_admin = bool(user and user.role in ("admin", "moderator"))
        return is_admin


class IsAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user and user.role == "user"


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        print("1")
        user = request.user
        return user and user.role == "user"
    
    def has_object_permission(self, request, view, obj):
        print("2)")
        user = request.user
        return user and obj.owner == user


class IsFollower(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user in obj.followers.all():
            return True
        return False
