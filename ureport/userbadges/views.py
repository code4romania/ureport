from dash.orgs.views import OrgPermsMixin, OrgObjPermsMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from smartmin.views import (
    SmartCRUDL,
    SmartListView,
    SmartUpdateView,
    SmartCreateView,
)

from ureport.apiextras.views import (
    IsOwnerUserOrAdmin,
    STORY_API_PATH, 
    USER_API_PATH, 
)
from ureport.userbadges.forms import BadgeTypeForm
from ureport.userbadges.serializers import (
    UserBadgeSerializer,
)
from ureport.userbadges.models import BadgeType, UserBadge
   

class BadgeTypeCRUDL(SmartCRUDL):
    model = BadgeType
    actions = ("create", "update", "list")

    class Update(OrgObjPermsMixin, SmartUpdateView):
        form_class = BadgeTypeForm
        fields = (
            "title", "image",
            "is_active", "validation_category", "validation_total",
            "unfinished_template", "finished_description",
        )

    class Create(OrgPermsMixin, SmartCreateView):
        form_class = BadgeTypeForm
        fields = (
            "org", "title", "image",
        )

    class List(OrgPermsMixin, SmartListView):
        fields = (
            "org", "title", "is_active", "validation_category", "validation_total",
        )
        ordering = ("org__name", "title")

        def get_queryset(self, **kwargs):
            queryset = super(BadgeTypeCRUDL.List, self).get_queryset(**kwargs)

            if self.derive_org():
                queryset = queryset.filter(org=self.derive_org())

            return queryset


class UserBadgeViewSet(ModelViewSet):
    """
    This endpoint allows you to manage the user badges


    Query filters:

    * **user** - the ID of the user that owns the badge
    * **org** - the ID of the Org which provides the badge type

    """
    
    serializer_class = UserBadgeSerializer
    queryset = UserBadge.visible.all()
    model = UserBadge
    permission_classes = [IsOwnerUserOrAdmin]

    def filter_queryset(self, queryset):
        user_id = self.request.query_params.get("user")
        org_id = self.request.query_params.get("org")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if org_id:
            queryset = queryset.filter(badge_type__org=org_id)

        return queryset

    @action(detail=False, methods=['get'], url_path=USER_API_PATH)
    def retrieve_user_badges(self, request, user_id):
        """
        Get the user badges belonging to the specified user (optionally filtered by Org)


        Example:

            GET /api/v1/userbadges/user/321/?org=1

        Result:

            [
                {
                    "id":1,
                    "badge_type":
                    {
                        "id":1,
                        "org":1,
                        "title":"First badge",
                        "image":"https://example.com/media/userbadges/icon.png",
                        "description":"You read your first story from this category!",
                        "validation_category":1,
                        "item_category":1,  # Deprecated
                    },
                    "user":321,
                    "offered_on":"2023-03-07T20:56:53.198494+02:00"
                }
            ]
        """
        
        queryset = self.get_queryset().filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = UserBadgeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
