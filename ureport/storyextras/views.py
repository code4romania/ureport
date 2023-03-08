# from django import forms
from django.http import Http404
# from dash.categories.fields import CategoryChoiceField
# from dash.orgs.views import OrgObjPermsMixin
# from dash.stories.views import StoryCRUDL, StoryForm
from dash.stories.models import Story, Category
from rest_framework import status
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
# from smartmin.views import SmartUpdateView

from ureport.apiextras.views import (
    IsOwnerUserOrAdmin,
    USER_API_PATH, 
    STORY_API_PATH,
)
from ureport.storyextras.models import (
    StoryBookmark, 
    StoryRating, 
    StoryRead, 
    StoryReward,
    StorySettings,
)
from ureport.storyextras.serializers import (
    StoryBookmarkSerializer,
    StoryBookmarkDetailedSerializer,
    StoryRatingSerializer,
    StoryRatingDetailedSerializer,
    StoryReadActionSerializer,
    StoryReadActionDetailedSerializer,
    StoryRewardSerializer,
    StoryRewardDetailedSerializer,
    StorySettingsSerializer,
)
from ureport.userbadges.models import create_badge_for_story
from ureport.userbadges.serializers import UserBadgeSerializer


# class ExtendedStoryForm(StoryForm):
#     """
#     Extend the standard StoryForm to also include the Story Settings
#     """
#     # TODO
#     category = CategoryChoiceField(Category.objects.none())

#     # def __init__(self, *args, **kwargs):
#     #     self.org = kwargs["org"]
#     #     del kwargs["org"]
#     #     super(ExtendedStoryForm, self).__init__(*args, **kwargs)

#     #     # We show all categories even inactive one in the dropdown
#     #     qs = Category.objects.filter(org=self.org).order_by("name")
#     #     self.fields["category"].queryset = qs

#     class Meta:
#         model = Story
#         fields = (
#             "is_active",
#             "title",
#             "featured",
#             "summary",
#             "content",
#             "attachment",
#             "written_by",
#             "audio_link",
#             "video_id",
#             "tags",
#             "category",
#             "storysettings",
#         )


# class ExtendedStoryCRUDL(StoryCRUDL):
#     """
#     Extend the standard StoryCRUDL to also include the Story Settings
#     """
#     # TODO
#     model = Story
#     actions = ("create", "update", "list", "images")

#     class Update(OrgObjPermsMixin, SmartUpdateView):
#         form_class = ExtendedStoryForm
#         fields = (
#             "is_active",
#             "title",
#             "featured",
#             "summary",
#             "content",
#             "attachment",
#             "written_by",
#             "audio_link",
#             "video_id",
#             "tags",
#             "category",
#             "storysettings",
#         )

#         def pre_save(self, obj):
#             obj = super(ExtendedStoryCRUDL.Update, self).pre_save(obj)
#             obj.audio_link = Story.format_audio_link(obj.audio_link)
#             obj.tags = Story.space_tags(obj.tags)
#             return obj

#         def get_form_kwargs(self):
#             kwargs = super(ExtendedStoryCRUDL.Update, self).get_form_kwargs()
#             kwargs["org"] = self.request.org
#             return kwargs

#     def url_name_for_action(self, action):
#         """
#         Patch the reverse name for this action to match the original "stories"
#         """
#         return "%s.%s_%s" % ("stories", self.model_name.lower(), action)


class TempViewSet(ModelViewSet):
    """ TODO: REMOVE THIS TEMPORARY ENDPOINT """
    serializer_class = StoryBookmarkSerializer
    queryset = StoryBookmark.objects.all()
    model = StoryBookmark
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path="myid/")
    def my_user_id(self, request):
        """
        TODO: This is a temporary function which returns the current user id
        """
        return Response({'id': request.user.id})


class StorySettingsViewSet(ModelViewSet):
    serializer_class = StorySettingsSerializer
    queryset = StorySettings.objects.all()
    model = StorySettings
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'], url_path=STORY_API_PATH)
    def retrieve_settings(self, request, story_id):
        """
        Get the settings for the current story
        """
        try:
            story = Story.objects.get(pk=story_id)
        except Story.DoesNotExist:
            raise Http404

        settings, _ = StorySettings.objects.get_or_create(story=story)
        serializer = StorySettingsSerializer(settings, many=False)
        return Response(serializer.data)



class StoryBookmarkViewSet(ModelViewSet):
    """
    This endpoint allows you to manage the story bookmarks.

    ## Listing story bookmarks

    By making a ```GET``` request you can list all the story bookmarks for all organizations, filtering them as needed.
    
    ### Query filters:

    * **user** - the ID of the user that set the bookmark (int)
    * **story** - the ID of the story for which the bookmark was set (int)

    Each story bookmark has the following attributes:

    * **id** - the ID of the item (int)
    * **user** - the ID of the user that set the bookmark (int)
    * **story** - the ID of the story for which the bookmark was set (int)

    Example:

        GET /api/v1/storybookmarks/

    Response is the list of story bookmarks for all organizations, most recent first:

        {
            "count": 389,
            "next": "/api/v1/storybookmarks/?page=2",
            "previous": null,
            "results": [
            {
                "id": 1,
                "user": 7,
                "story": 434
            },
            ...
        }
    """
    
    serializer_class = StoryBookmarkSerializer
    queryset = StoryBookmark.objects.all()
    model = StoryBookmark
    permission_classes = [IsOwnerUserOrAdmin]

    def filter_queryset(self, queryset):
        user_id = self.request.query_params.get("user")
        story_id = self.request.query_params.get("story")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if story_id:
            queryset = queryset.filter(story_id=story_id)

        return queryset

    @action(detail=False, methods=['get'], url_path=USER_API_PATH)
    def retrieve_user_bookmarks(self, request, user_id):
        """
        Get the bookmarks for the current user
        """

        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = StoryBookmarkDetailedSerializer(filtered_queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path=USER_API_PATH)
    def remove_user_bookmarks(self, request, user_id):
        """
        Remove any bookmarks of the current user
        """

        count = StoryBookmark.objects.filter(
            story_id=request.data.get("story"),
            user_id=user_id
        ).delete()
        return Response({"count": count[0]})

    @action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def create_user_bookmark(self, request, user_id):
        """
        Bookmark a story for the current user
        """

        data = {
            'story': request.data.get("story"),
            'user': user_id,
        }
        serializer = StoryBookmarkSerializer(data=data)

        try:
            bookmark = StoryBookmark.objects.get(
                user=data["user"],
                story=data["story"],
            )
            serializer = StoryBookmarkSerializer(bookmark, data=data, partial=True)
            created = False
        except StoryBookmark.DoesNotExist:
            serializer = StoryBookmarkSerializer(data=data)
            created = True

        if serializer.is_valid():
            bookmark = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            StoryBookmarkDetailedSerializer(bookmark).data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class StoryRatingViewSet(ModelViewSet):
    """
    This endpoint allows you to manage the story ratings


    Query filters:

    * **user** - the ID of the user that set the rating (int)
    * **story** - the ID of the story for which the rating was set (int)

    """
    
    serializer_class = StoryRatingSerializer
    queryset = StoryRating.objects.all()
    model = StoryRating
    permission_classes = [IsOwnerUserOrAdmin]

    def filter_queryset(self, queryset):
        user_id = self.request.query_params.get("user")
        story_id = self.request.query_params.get("story")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if story_id:
            queryset = queryset.filter(story_id=story_id)

        return queryset

    @action(detail=False, methods=['get'], url_path=USER_API_PATH)
    def retrieve_user_ratings(self, request, user_id):
        """
        Get the ratings given by the current user
        """
        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = StoryRatingDetailedSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def set_user_rating(self, request, user_id):
        """
        Create or update a rating given by the current user
        """
        data = {
            'user': user_id,
            'story': request.data.get("story"),
            'score': request.data.get("score"),
        }

        try:
            rating = StoryRating.objects.get(
                user=data["user"],
                story=data["story"],
            )
            serializer = StoryRatingSerializer(rating, data=data, partial=True)
            created = False
        except StoryRating.DoesNotExist:
            serializer = StoryRatingSerializer(data=data)
            created = True

        if serializer.is_valid():
            rating = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            StoryRatingDetailedSerializer(rating).data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class StoryReadActionViewSet(ModelViewSet):
    """
    This endpoint allows you to manage the story read actions


    Query filters:

    * **user** - the ID of the user that read the story (int)
    * **story** - the ID of the story which was read by the user (int)

    """
    
    serializer_class = StoryReadActionSerializer
    queryset = StoryRead.objects.all()
    model = StoryRead
    permission_classes = [IsOwnerUserOrAdmin]

    def filter_queryset(self, queryset):
        user_id = self.request.query_params.get("user")
        story_id = self.request.query_params.get("story")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if story_id:
            queryset = queryset.filter(story_id=story_id)

        return queryset

    @action(detail=False, methods=['get'], url_path=USER_API_PATH)
    def retrieve_user_reads(self, request, user_id):
        """
        Get the story reads by the current user
        """
        
        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = StoryReadActionDetailedSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def set_user_read(self, request, user_id):
        """
        Mark a story as read by the current user and return a list of earned badges (if any)
        """
        
        data = {
            'story': request.data.get("story"),
            'user': user_id,
        }

        try:
            read = StoryRead.objects.get(
                user=data["user"],
                story=data["story"],
            )
            serializer = StoryReadActionSerializer(read, data=data, partial=True)
            created = False
        except StoryRead.DoesNotExist:
            serializer = StoryReadActionSerializer(data=data)
            created = True

        if serializer.is_valid():
            read = serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Count how many stories the user has read
        total_reads = StoryRead.objects.filter(
            user=read.user, story__org=read.story.org).count()
        category_reads = StoryRead.objects.filter(
            user=read.user, story__category=read.story.category).count()

        new_badges = create_badge_for_story(
            read.user, read.story.org, read.story.category, total_reads, category_reads)

        # show the new badges
        badges_serializer = UserBadgeSerializer(new_badges, many=True)
        return Response(
            badges_serializer.data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class StoryRewardViewSet(ModelViewSet):
    """
    This endpoint allows you to manage the story rewards


    Query filters:

    * **user** - the ID of the user that received the reward (int)
    * **story** - the ID of the story for which the reward was given (int)

    """
    
    serializer_class = StoryRewardSerializer
    queryset = StoryReward.objects.all()
    model = StoryReward
    permission_classes = [IsOwnerUserOrAdmin]

    def filter_queryset(self, queryset):
        user_id = self.request.query_params.get("user")
        story_id = self.request.query_params.get("story")
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if story_id:
            queryset = queryset.filter(story_id=story_id)

        return queryset

    @action(detail=False, methods=['get'], url_path=USER_API_PATH)
    def retrieve_user_rewards(self, request, user_id):
        """
        Get the rewards received by the current user
        """
        
        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        serializer = StoryRewardDetailedSerializer(filtered_queryset, many=True)
        return Response(serializer.data)
