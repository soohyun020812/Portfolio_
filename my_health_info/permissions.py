from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    본인이 작성한 루틴에 대해서만 변경 권한을 허용합니다.
    """

    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모두에게 허용하므로,
        # GET, HEAD 또는 OPTIONS 요청은 항상 허용됩니다.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 권한은 해당 루틴의 작성자에게만 허용됩니다.
        return obj.author == request.user
