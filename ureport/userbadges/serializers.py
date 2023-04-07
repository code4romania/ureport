from rest_framework import serializers

from ureport.userbadges.models import BadgeType, UserBadge
from ureport.storyextras.models import StoryRead, CategoryExtras


class BadgeTypeSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    item_category = serializers.CharField(source="validation_category_id")  # Deprecated field

    class Meta:
        model = BadgeType
        fields = ("id", "org", "title", "image", "description", "validation_category", "item_category")

    def get_description(self, badge_type: BadgeType) -> str:
        return badge_type.get_description()


class UserBadgeTypeSerializer(BadgeTypeSerializer):
    """
    This serializer needs the user_id, org_id, and owned_type_ids provided in the context
    """
    owned = serializers.SerializerMethodField()

    class Meta:
        model = BadgeType
        fields = ("id", "org", "title", "image", "description", "validation_category", "owned")

    def get_owned(self, badge_type: BadgeType) -> bool:
        if badge_type.id in self.context.get("owned_type_ids", []):
            return True
        else:
            return False

    def get_description(self, badge_type: BadgeType) -> str:
        user_id = self.context.get("user_id", 0)
        org_id = self.context.get("org_id", 0)
        owned_ids = self.context.get("owned_type_ids", [])
        
        # TODO: pass the story read counts per org and per category from a cached location
        if not badge_type.validation_category:
            # calculate Reads per Org
            read_count = StoryRead.objects.filter(user_id=user_id, story__org_id=org_id).count()
        else:
            # calculate Reads per Category or Subcategory
            subcategory_ids = CategoryExtras.get_subcategory_ids(badge_type.validation_category)
            read_count = StoryRead.objects.filter(
                user_id=user_id, 
                story__category__in=[badge_type.validation_category.pk]+subcategory_ids
            ).count()

        if badge_type.id in owned_ids:
            return badge_type.get_description(finished=True)
        else:
            return badge_type.get_description(read_count, finished=False)


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_type = BadgeTypeSerializer()

    class Meta:
        model = UserBadge
        fields = ("id", "badge_type", "user", "offered_on")
