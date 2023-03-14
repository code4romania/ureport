from rest_framework.permissions import IsAuthenticated, IsAdminUser


CURRENT_USER_API_PATH =  "user/@me/"
USER_API_PATH = "user/(?P<user_id>[\d]+)"
STORY_API_PATH = "story/(?P<story_id>[\d]+)"
USER_STORY_API_PATH = "{}/{}".format(USER_API_PATH, STORY_API_PATH)


class IsOwnerUserOrAdmin(IsAuthenticated):
    """
    Only allow staff members or authenticated users who own the object
    """
    def has_permission(self, request, view):
        """
        For non-staff, check that the URL user is the same as the authenticated user
        """
        
        try:
            url_user_id = int(view.kwargs.get("user_id", 0))
        except ValueError:
            url_user_id = None

        if request.user.is_staff or url_user_id == request.user.id:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        """
        For non-staff, check that the object owner user is the same as the authenticated user
        """
        if request.user.is_staff or obj.user == request.user:
            return True
        else:
            return False
