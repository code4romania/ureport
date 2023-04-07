from dash.orgs.views import OrgPermsMixin, OrgObjPermsMixin
from django.http import HttpRequest, HttpResponse
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
    UserBadgeTypeSerializer,
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
    def retrieve_user_badges(self, request: HttpRequest, user_id: int) -> HttpResponse:
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
                },
                ...
            ]
        """
        
        queryset = self.get_queryset().filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = UserBadgeSerializer(filtered_queryset, many=True)
        return Response(serializer.data)


    @action(detail=False, methods=['get'], url_path=USER_API_PATH)
    def retrieve_user_badge_types(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Get all badge types and their progress for the specified user (optionally filtered by Org)


        Example:

            GET /api/v1/userbadges/user/321/all/?org=1

        Result:

            [
                {
                    "id":1,
                    "org":1,
                    "title":"First badge",
                    "image":"https://example.com/media/userbadges/icon.png",
                    "description":"You have 5 more stories to read in order to receive this badge.",
                    "validation_category":1,
                    "owned":true
                },
                ...
            ]
        """
        
        queryset = BadgeType.visible.all()
        
        org_id = self.request.query_params.get("org")
        if org_id:
            filtered_queryset = queryset.filter(org=org_id)
        else:
            filtered_queryset = queryset
        
        context = {
            "user_id": request.user.id,
            "org_id": org_id,
            "owned_type_ids": list(  # TODO: Cache this!
                UserBadge.objects.filter(user_id=user_id).values_list("badge_type_id", flat=True))
        }
        serializer = UserBadgeTypeSerializer(filtered_queryset, many=True, context=context)

        return Response(serializer.data)
