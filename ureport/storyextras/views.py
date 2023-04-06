# from django import forms
from django.http import Http404, HttpRequest, HttpResponse
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
from ureport.userbadges.models import UserBadge
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


class StorySettingsViewSet(ModelViewSet):
    serializer_class = StorySettingsSerializer
    queryset = StorySettings.objects.all()
    model = StorySettings
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'], url_path=STORY_API_PATH)
    def retrieve_settings(self, request: HttpRequest, story_id: int) -> HttpResponse:
        """
        Retrieve the settings for the specified story


        Example:

            GET /api/v1/storysettings/story/123/

        Response:
            
            {
                "display_rating":true,
                "rating":"5.00"
            }
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
    def retrieve_user_bookmarks(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Retrieve the bookmarks set by the specified user


        Example:

            GET /api/v1/storybookmarks/user/321/

        You may also filter by story:
            
            GET /api/v1/storybookmarks/user/321/?story=1

        Response will also contain some details about the bookmarked story:
            
            [
                {
                    "id":13,
                    "user":321,
                    "story": {
                        "id":1,
                        "title":"Test Story",
                        "featured":false,
                        "summary":"asdasdasd asdasd asd",
                        "video_id":null,
                        "audio_link":null,
                        "tags":null,
                        "org":1,
                        "images":[],
                        "created_on":"2023-01-30T13:56:31.493752+02:00"
                    }
                }
            ]
        """

        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        context = {"request": request}
        serializer = StoryBookmarkDetailedSerializer(filtered_queryset, many=True, context=context)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path=USER_API_PATH)
    def remove_user_bookmarks(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Remove any bookmarks set by the specified user

        Example:
        
            DELETE /api/v1/storybookmarks/user/321/

        Data:

            {
                "story": 1
            }

        Result contains the number of deleted items: 
        
            {
                "count":1
            }

        """

        count = StoryBookmark.objects.filter(
            story_id=request.data.get("story"),
            user_id=user_id
        ).delete()
        return Response({"count": count[0]})

    @action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def create_user_bookmark(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Bookmark a story for the specified user

        Example:
            
            POST /api/v1/storybookmarks/user/321/

        Data:

            {
                "story": 1
            }

        Response will contain some details about the bookmarked story:
            
            {
                "id":13,
                "user":321,
                "story": {
                    "id":1,
                    "title":"Test Story",
                    "featured":false,
                    "summary":"asdasdasd asdasd asd",
                    "video_id":null,
                    "audio_link":null,
                    "tags":null,
                    "org":1,
                    "images":[],
                    "created_on":"2023-01-30T13:56:31.493752+02:00"
                }
            }
        """

        data = {
            'story': request.data.get("story"),
            'user': user_id,
        }
        serializer = StoryBookmarkSerializer(data=data)
        context = {"request": request}
        
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
            StoryBookmarkDetailedSerializer(bookmark, context=context).data, 
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
    def retrieve_user_ratings(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Get the ratings given by the specified user (optionally filtered by Story)


        Example:

            GET /api/v1/storyratings/user/321/?story=1

        Data:

            -

        Result will contain the ratings and some details about the rated stories:

            [
                {
                    "id":2,
                    "user":321,
                    "score":4,
                    "story":
                    {
                        "id":1,
                        "title":"Test Story",
                        "featured":false,
                        "summary":"asdasdasd asdasd asd",
                        "video_id":null,
                        "audio_link":null,
                        "tags":null,
                        "org":1,
                        "images":[],
                        "created_on":"2023-01-30T13:56:31.493752+02:00"
                    }
                }
            ]
        """

        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        context = {"request": request}
        serializer = StoryRatingDetailedSerializer(filtered_queryset, many=True, context=context)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def set_user_rating(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Create or update a story rating given by the specified user

        
        Example:
        
            POST /api/v1/storyratings/user/321/

        Data:

            {
                "story": 1,
                "score":5
            }

        Result will contain the rating and some details about the rated story:

            {
                "id":2,
                "user":321,
                "score":4,
                "story":
                {
                    "id":1,
                    "title":"Test Story",
                    "featured":false,
                    "summary":"asdasdasd asdasd asd",
                    "video_id":null,
                    "audio_link":null,
                    "tags":null,
                    "org":1,
                    "images":[],
                    "created_on":"2023-01-30T13:56:31.493752+02:00"
                }
            }
        """

        data = {
            'user': user_id,
            'story': request.data.get("story"),
            'score': request.data.get("score"),
        }
        context = {"request": request}

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
            StoryRatingDetailedSerializer(rating, context=context).data, 
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
    def retrieve_user_reads(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Get the story reads by the specified user

        
        
        Example:

            GET /api/v1/storyreads/user/321/

        Data:

            -

        Result will contain the read stories and some details about them:

            [
                {
                    "id":1,
                    "user":321,
                    "story":
                    {
                        "id":1,
                        "title":"Test Story",
                        "featured":false,
                        "summary":"asdasdasd asdasd asd",
                        "video_id":null,
                        "audio_link":null,
                        "tags":null,
                        "org":1,
                        "images":[],
                        "created_on":"2023-01-30T13:56:31.493752+02:00"
                    }
                }
            ]
        """
        
        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        context = {"request": request}
        serializer = StoryReadActionDetailedSerializer(filtered_queryset, context=context, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def set_user_read(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Mark a story as read by the specified user and return a list of earned badges (if any)

        
        Example:

            POST /api/v1/storyreads/user/321/

        Data:

            {
                "story": 1
            }

        Result will contain a list of newly earned badges:

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
                        "item_category":1
                    },
                    "user":321,
                    "offered_on":"2023-03-07T20:56:53.198494+02:00"
                }
            ]
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

        new_badges = UserBadge.create_badges_after_story(
            read.user, read.story.org, read.story.category)

        # show the new badges
        badges_serializer = UserBadgeSerializer(new_badges, many=True)
        return Response(
            badges_serializer.data, 
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=False, methods=['delete'], url_path=USER_API_PATH)
    def reset_user_reads(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Delete the read story stats including received badges and rewards
        
        
        Example:

            DELETE /api/v1/storyreads/user/321/

        Data:

            -

        Result will contain the number of deleted items:

            {
                "read_count":12,
                "reward_count":7,
                "badge_count":3,
            }
        """
                
        read_count = StoryRead.objects.filter(
            user_id=user_id
        ).delete()

        reward_count = StoryReward.objects.filter(
            user_id=user_id
        ).delete()

        badge_count = UserBadge.objects.filter(
            user_id=user_id
        ).delete()

        return Response({
            "read_count": read_count[0],
            "reward_count": reward_count[0],
            "badge_count": badge_count[0],
        })


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
    def retrieve_user_rewards(self, request: HttpRequest, user_id: int) -> HttpResponse:
        """
        Get the rewards received by the specified user for reading stories
        
        
        Example:

            GET /api/v1/storyrewards/user/321/

        Data:

            -

        Result will contain the rewards and some details about the read stories:

            [
                {
                    "id":1,
                    "user":321,
                    "points":100,
                    "story":
                    {
                        "id":1,
                        "title":"Test Story",
                        "featured":false,
                        "summary":"asdasdasd asdasd asd",
                        "video_id":null,
                        "audio_link":null,
                        "tags":null,
                        "org":1,
                        "images":[],
                        "created_on":"2023-01-30T13:56:31.493752+02:00"
                    }
                }
            ]
        """
        
        queryset = self.model.objects.filter(user_id=user_id)
        filtered_queryset = self.filter_queryset(queryset)
        context = {"request": request}
        serializer = StoryRewardDetailedSerializer(filtered_queryset, context=context, many=True)
        return Response(serializer.data)

