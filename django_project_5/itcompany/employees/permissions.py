from rest_framework import permissions


class IsVisitor(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS 


class IsWatchman(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ["PUT", "PATCH"]:
            return request.user.is_authenticated

        return False


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class EmployeePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        if request.user.is_staff:
            return True

        if request.method in ["PUT", "PATCH"]:
            return request.user.is_authenticated

        return False


class WorkplacePermissions(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        if request.method in ["PUT", "PATCH"]:
            return request.user.is_authenticated

        if request.method in ["POST", "DELETE"]:
            return request.user.is_staff

        return False
