# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from rest_framework_swagger.views import get_swagger_view

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

schema_view = get_swagger_view(title="API")


urlpatterns = [
    re_path(r"^$", RedirectView.as_view(pattern_name="api.v1.docs", permanent=False), name="api.v1"),
    re_path(r"^docs/", schema_view, name="api.v1.docs"),
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
    re_path(r"^categories/org/(?P<org>[\d]+)/$", CategoryList.as_view(), name="api.v1.org_category_list"),
    re_path(r"^categories/(?P<pk>[\d]+)/$", CategoryDetails.as_view(), name="api.v1.category_details"),
]
