from rest_framework import serializers

from ureport.userbadges.models import BadgeType, UserBadge


class BadgeTypeSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    item_category = serializers.CharField(source="validation_category_id")  # Deprecated field

    class Meta:
        model = BadgeType
        fields = ("id", "org", "title", "image", "description", "validation_category", "item_category")

    def get_description(self, badge_type: BadgeType) -> str:
        # TODO: extend serializer context in order to be able to pass the story read counts
        return badge_type.get_description()


class UserBadgeSerializer(serializers.ModelSerializer):
    badge_type = BadgeTypeSerializer()

    class Meta:
        model = UserBadge
        fields = ("id", "badge_type", "user", "offered_on")
