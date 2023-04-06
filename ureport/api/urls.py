# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework_swagger.views import get_swagger_view
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from django.urls import re_path
from django.views.generic import RedirectView

from ureport.api.views import (
    CategoryDetails,
    CategoryList,
    DashBlockDetails,
    DashBlockList,
    FeaturedPollList,
    ImageDetails,
    ImageList,
    NewsItemDetails,
    NewsItemList,
    OrgDetails,
    OrgList,
    PollDetails,
    PollList,
    StoryDetails,
    StoryList,
    VideoDetails,
    VideoList,
)
from ureport.storyextras.views import (
    StoryBookmarkViewSet,
    StoryRatingViewSet,
    StoryReadActionViewSet,
    StoryRewardViewSet,
    StorySettingsViewSet,
)
from ureport.userbadges.views import UserBadgeViewSet
from ureport.userprofiles.views import CustomAuthToken, UserProfileViewSet, social_registration


schema_view = get_swagger_view(title="API")


urlpatterns = [
    re_path(r"^$", RedirectView.as_view(pattern_name="api.v1.docs", permanent=False), name="api.v1"),
    # re_path(r"^docs/", schema_view, name="api.v1.docs"),  # Obsolete
    re_path(r"^orgs/$", OrgList.as_view(), name="api.v1.org_list"),
    re_path(r"^orgs/(?P<pk>[\d]+)/$", OrgDetails.as_view(), name="api.v1.org_details"),
    re_path(r"^polls/org/(?P<org>[\d]+)/$", PollList.as_view(), name="api.v1.org_poll_list"),
    re_path(r"^polls/org/(?P<org>[\d]+)/featured/$", FeaturedPollList.as_view(), name="api.v1.org_poll_fetured"),
    re_path(r"^polls/(?P<pk>[\d]+)/$", PollDetails.as_view(), name="api.v1.poll_details"),
    re_path(r"^news/org/(?P<org>[\d]+)/$", NewsItemList.as_view(), name="api.v1.org_newsitem_list"),
    re_path(r"^news/(?P<pk>[\d]+)/$", NewsItemDetails.as_view(), name="api.v1.newsitem_details"),
    re_path(r"^videos/org/(?P<org>[\d]+)/$", VideoList.as_view(), name="api.v1.org_video_list"),
    re_path(r"^videos/(?P<pk>[\d]+)/$", VideoDetails.as_view(), name="api.v1.video_details"),
    re_path(r"^assets/org/(?P<org>[\d]+)/$", ImageList.as_view(), name="api.v1.org_asset_list"),
    re_path(r"^assets/(?P<pk>[\d]+)/$", ImageDetails.as_view(), name="api.v1.asset_details"),
    re_path(r"^dashblocks/org/(?P<org>[\d]+)/$", DashBlockList.as_view(), name="api.v1.org_dashblock_list"),
    re_path(r"^dashblocks/(?P<pk>[\d]+)/$", DashBlockDetails.as_view(), name="api.v1.dashblock_details"),
    re_path(r"^stories/org/(?P<org>[\d]+)/$", StoryList.as_view(), name="api.v1.org_story_list"),
    re_path(r"^stories/(?P<pk>[\d]+)/$", StoryDetails.as_view(), name="api.v1.story_details"),
    
    # Authentication
    re_path(r"^get-auth-token/facebook/$", social_registration, {"backend": "facebook-oauth2"}),
    re_path(r"^get-auth-token/google/$", social_registration, {"backend": "google-oauth2"}),
    re_path(r"^get-auth-token/", CustomAuthToken.as_view()),

    # Swagger UI for documentation
    re_path(r"^swagger/schema/", SpectacularAPIView.as_view(), name="api.v1.schema"),
    re_path(r"^swagger/", SpectacularSwaggerView.as_view(url_name='api.v1.schema'), name='swagger-ui'),

    # Categories API extension:
    re_path(r"^categories/org/(?P<org>[\d]+)/$", CategoryList.as_view(), name="api.v1.org_category_list"),
    re_path(r"^categories/(?P<pk>[\d]+)/$", CategoryDetails.as_view(), name="api.v1.category_details"),

    # StorySettings API
    re_path(
        r"^storysettings/story/(?P<story_id>[\d]+)/$", 
        StorySettingsViewSet.as_view({
            "get": "retrieve_settings",
        }), 
        name="api.v1.storysettings_for_story"
    ),

    # StoryBookmarks API
    re_path(
        r"^storybookmarks/$", 
        StoryBookmarkViewSet.as_view({
            "get": "list", 
            "post": "create",
        }), 
        name="api.v1.storybookmarks_list"
    ),
    re_path(
        r"^storybookmarks/(?P<pk>[\d]+)/$", 
        StoryBookmarkViewSet.as_view({
            "get": "retrieve",
            # "put": "update",
            # "patch": "partial_update",
            "delete": "destroy",
        }), 
        name="api.v1.storybookmarks_detail"
    ),
    re_path(
        r"^storybookmarks/user/(?P<user_id>[\d]+)/$", 
        StoryBookmarkViewSet.as_view({
            "get": "retrieve_user_bookmarks",
            "post": "create_user_bookmark",
            "delete": "remove_user_bookmarks",
        }), 
        name="api.v1.storybookmarks_for_user"
    ),

    # StoryRatings API
    re_path(
        r"^storyratings/$", 
        StoryRatingViewSet.as_view({
            "get": "list", 
            "post": "create",
        }), 
        name="api.v1.storyratings_list"
    ),
    re_path(
        r"^storyratings/(?P<pk>[\d]+)/$", 
        StoryRatingViewSet.as_view({
            "get": "retrieve",
            # "put": "update",
            # "patch": "partial_update",
            "delete": "destroy",
        }), 
        name="api.v1.storyratings_detail"
    ),
    re_path(
        r"^storyratings/user/(?P<user_id>[\d]+)/$",
        StoryRatingViewSet.as_view({
            "get": "retrieve_user_ratings",
            "post": "set_user_rating",
        }), 
        name="api.v1.storyratings_for_user"
    ),

    # StoryReads API
    re_path(
        r"^storyreads/$", 
        StoryReadActionViewSet.as_view({
            "get": "list", 
            "post": "create",
        }), 
        name="api.v1.storyreads_list"
    ),
    re_path(
        r"^storyreads/(?P<pk>[\d]+)/$", 
        StoryReadActionViewSet.as_view({
            "get": "retrieve",
            # "put": "update",
            # "patch": "partial_update",
            "delete": "destroy",
        }), 
        name="api.v1.storyreads_detail"
    ),
    re_path(
        r"^storyreads/user/(?P<user_id>[\d]+)/$",
        StoryReadActionViewSet.as_view({
            "get": "retrieve_user_reads",
            "delete": "reset_user_reads",
            "post": "set_user_read",
        }), 
        name="api.v1.storyreads_for_user"
    ),

    # StoryRewards API
    re_path(
        r"^storyrewards/$", 
        StoryRewardViewSet.as_view({
            "get": "list", 
            "post": "create",
        }), 
        name="api.v1.storyrewards_list"
    ),
    re_path(
        r"^storyrewards/(?P<pk>[\d]+)/$", 
        StoryRewardViewSet.as_view({
            "get": "retrieve",
            # "put": "update",
            # "patch": "partial_update",
            "delete": "destroy",
        }), 
        name="api.v1.storyrewards_detail"
    ),
    re_path(
        r"^storyrewards/user/(?P<user_id>[\d]+)/$",
        StoryRewardViewSet.as_view({
            "get": "retrieve_user_rewards",
        }), 
        name="api.v1.storyrewards_for_user"
    ),

    # UserBadges API
    re_path(
        r"^userbadges/$", 
        UserBadgeViewSet.as_view({
            "get": "list", 
            "post": "create",
        }), 
        name="api.v1.userbadges_list"
    ),
    re_path(
        r"^userbadges/(?P<pk>[\d]+)/$", 
        UserBadgeViewSet.as_view({
            "get": "retrieve",
            # "put": "update",
            # "patch": "partial_update",
            "delete": "destroy",
        }), 
        name="api.v1.userbadges_detail"
    ),
    re_path(
        r"^userbadges/user/(?P<user_id>[\d]+)/$",
        UserBadgeViewSet.as_view({
            "get": "retrieve_user_badges",
        }), 
        name="api.v1.userbadges_for_user"
    ),

    # UserProfiles API
    re_path(
        r"^userprofiles/signup/$", 
        UserProfileViewSet.as_view({
            "post": "create_user",
        }),
        name="api.v1.userprofiles_signup"
    ),
    re_path(
        r"^userprofiles/forgot/$", 
        UserProfileViewSet.as_view({
            "post": "reset_password",
        }),
        name="api.v1.userprofiles_forgot_initial"
    ),
    re_path(
        r"^userprofiles/forgot/check/$", 
        UserProfileViewSet.as_view({
            "post": "reset_password",
        }),
        name="api.v1.userprofiles_forgot_check"
    ),
    re_path(
        r"^userprofiles/forgot/password/$", 
        UserProfileViewSet.as_view({
            "post": "reset_password",
        }),
        name="api.v1.userprofiles_forgot_change"
    ),
    re_path(
        r"^userprofiles/user/(?P<user_id>[\d]+)/password/$", 
        UserProfileViewSet.as_view({
            "post": "change_password",
        }),
        name="api.v1.userprofiles_change_password"
    ),
    re_path(
        r"^userprofiles/user/@me/$",
        UserProfileViewSet.as_view({
            "get": "retrieve_current_user_with_profile",
        }), 
        name="api.v1.userprofiles_current"
    ),
    re_path(
        r"^userprofiles/user/(?P<user_id>[\d]+)/$",
        UserProfileViewSet.as_view({
            "get": "retrieve_user_with_profile",
            "patch": "partial_update",
            "delete": "delete_user",
        }), 
        name="api.v1.userprofiles_as_user"
    ),
    re_path(
        r"^userprofiles/user/(?P<user_id>[\d]+)/image/$",
        UserProfileViewSet.as_view({
            "put": "update_image",
        }), 
        name="api.v1.userprofiles_image"
    ),
]
