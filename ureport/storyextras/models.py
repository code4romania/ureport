from typing import Optional, List

from dash.stories.models import Story, Category
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class StorySettings(models.Model):
    """ Various settings per Story """
    
    story = models.OneToOneField(
        Story,
        verbose_name=_("Story"), on_delete=models.CASCADE)
    reward_points = models.PositiveSmallIntegerField(
        verbose_name=_("Reward points"),
        default=0, blank=False, null=False,
        help_text=_("How many points does an user earn for reading this story"))
    display_rating = models.BooleanField(
        verbose_name=_("Display the user rating"), default=True,
        help_text=_("Display or hide the user rating for this story"))
    rating = models.DecimalField(
        verbose_name=_("Average rating"),
        max_digits=5, decimal_places=2, default=0, editable=False,
        help_text=_("Cached computed rating average"))

    class Meta:
        verbose_name = _("Story settings")
        verbose_name_plural = _("Story settings")


@receiver(post_save, sender=Story)
def auto_create_story_settings(sender, instance, **kwargs):
    if not StorySettings.objects.filter(story=instance).exists():
        try:
            StorySettings.objects.create(story=instance)
        except IntegrityError:
            pass


class StoryUserModel(models.Model):
    """ Common fields for keeping user data about specific stories """
    
    story = models.ForeignKey(
        Story, verbose_name=_("Story"), blank=False, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name=_("User"), blank=False, null=False, on_delete=models.CASCADE)
    created_on = models.DateTimeField(
        verbose_name=_("Creation date"), auto_now_add=timezone.now, editable=False)

    class Meta:
        abstract = True


class StoryBookmark(StoryUserModel):
    """ An user bookmark flag for a specific story """

    class Meta:
        verbose_name = _("Story bookmark")
        verbose_name_plural = _("Story bookmarks")
        unique_together = ['story', 'user']


class StoryRating(StoryUserModel):
    """ An user rating for a specific story """

    score = models.PositiveSmallIntegerField(
        verbose_name=_("Score"),
        default=1, blank=False, null=False,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name = _("Story rating")
        verbose_name_plural = _("Story ratings")
        unique_together = ['story', 'user']


@receiver(post_save, sender=StoryRating)
def update_story_average_rating(sender, instance, **kwargs):
    average = StoryRating.objects.filter(
        story=instance.story).aggregate(models.Avg('score'))['score__avg']
    instance.story.storysettings.rating = round(average)
    instance.story.storysettings.save()
    

class StoryRead(StoryUserModel):
    """ Save the date when the user first read a story """

    class Meta:
        verbose_name = _("Story read")
        verbose_name_plural = _("Story reads")
        unique_together = ['story', 'user']


class StoryReward(StoryUserModel):
    """ Reward points received by an user for reading a story """

    points = models.PositiveSmallIntegerField(
        verbose_name=_("Points"),
        default=0, blank=True, null=False,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("How many points will be awarded to the reader"))

    class Meta:
        verbose_name = _("Story reward")
        verbose_name_plural = _("Story rewards")
        unique_together = ['story', 'user']


@receiver(models.signals.post_save, sender=StoryRating)
def calculate_story_rating(sender, **kwargs):
    # TODO
    print("Someone rated a story...")


class CategoryExtras:
    
    @staticmethod
    def get_parent_category(subcategory: Category) -> Optional[Category]:
        """
        Returns the top-level parent category ID 

        Example: 

            For "Category One / Subcategory 123 / Abcdef" it will try to
            retrieve "Category One"
        """

        sep = settings.SUBCATEGORY_SEPARATOR

        if not subcategory or not sep in subcategory.name:
            return None

        parent_name = subcategory.name.split(sep)[0].strip()
        try:
            parent_category = Category.objects.get(name=parent_name)
        except Category.DoesNotExist:
            return None
        else:
            return parent_category
        
    @staticmethod
    def get_subcategory_ids(category: Category) -> List[Category]:
        """
        Returns the list of subcategory IDs, 
        but only if the provided category is not a subcategory too
        """
        
        sep = settings.SUBCATEGORY_SEPARATOR

        if not category or sep in category.name:
            return []

        subcategory_name_start = "{} {}".format(category.name, sep)
        return list(
            Category.objects.filter(
                name__startswith=subcategory_name_start
            ).values_list('pk', flat=True)
        )