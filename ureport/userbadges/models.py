import string
from functools import partial
from typing import List

from dash.categories.models import Category
from dash.orgs.models import Org
from dash.utils import generate_file_path
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ngettext_lazy, gettext_lazy as _
from smartmin.models import SmartModel, ActiveManager

from ureport.storyextras.models import StoryRead, CategoryExtras


class VisibleTypeManager(models.Manager):
    """ Filter to return only visible items """

    def get_queryset(self):
        return super().get_queryset().filter(badge_type__is_active=True)


class BadgeType(SmartModel):
    """ A badge which is offered by a specific organisation for reading stories """

    org = models.ForeignKey(
        Org, verbose_name=_("Organisation"),
        blank=False, null=False, on_delete=models.CASCADE)
    title = models.CharField(
        verbose_name=_("Title"),max_length=50, blank=False, null=False)
    image = models.ImageField(
        verbose_name=_("Image"), 
        blank=True, null=True,
        upload_to=partial(generate_file_path, "userbadges"), 
        help_text=_("The badge image file"))
    is_active = models.BooleanField(
        verbose_name=_("Display or hide this item"),
        default=False, db_index=True)
    validation_category = models.ForeignKey(
        Category, verbose_name=_("Validation category"),
        blank=True, null=True, on_delete=models.PROTECT,
        help_text=_("Restrict badge validation to a specific category"))
    validation_total = models.PositiveSmallIntegerField(
        verbose_name=_("Total count for validation"),
        default=10000, blank=False, null=False,
        validators=[MinValueValidator(1), MaxValueValidator(10000)],
        help_text=_("Offer this badge only to users who completed the specified number of items (from the selected category)"))
    unfinished_template = models.TextField(
        _("In-progress badge description template"), default="", blank=True, null=False,
        help_text=_(
            "Template for the text to be displayed for badges which have not been earned yet. "
            "Use ${read_count} ${left_count} ${pluralize_stories_read} ${pluralize_stories_left} as placeholders for "
            "the total number of items already read in category, the number of items left to be read, "
            "the translated plural form of the item type (story, article, ...)"
        ))
    finished_description = models.TextField(
        _("Completed badge description"), default="", blank=True, null=False,
        help_text=_("Text to be displayed for earned badges"))
    objects = models.Manager()
    visible = ActiveManager()

    class Meta:
        ordering = ("validation_total", )
        verbose_name = _("Badge type")
        verbose_name_plural = _("Badge types")
        unique_together = ("org", "title")

    def __str__(self):
        return self.title

    def clean(self):
        """
        Check that this bagde type belongs to the same Org as the validation category
        """

        if self.validation_category and self.validation_category.org != self.org:
            raise ValidationError(_("The selected category belongs to a different organisation"))

    def get_description(self, read_count: int=0, finished: bool=True) -> str:
        """
        Get the badge type description text 

        For earned badges we display the finished description text, 
        while for in-progress badges the unfinished_template is parsed 
        in order to display a dynamic text based on the number of stories read by the user.
        """

        left_count = self.get_left_count(read_count, finished)

        if not left_count:
            return self.finished_description

        pluralize_lazy = ngettext_lazy("story", "stories", "count")
        data = {
            "read_count": read_count,
            "left_count": left_count,
            "pluralize_stories_read": pluralize_lazy % {"count": read_count},
            "pluralize_stories_left": pluralize_lazy % {"count": left_count},
        }
        return string.Template(self.unfinished_template).safe_substitute(data)

    def get_left_count(self, read_count: int=0, finished: bool=True) -> int:
        """ 
        Returns the number of stories left to be read for the user to reach validation_total
        """

        if finished:
            return 0
        elif read_count > self.validation_total:
            return 0
        else:
            return self.validation_total - read_count


class UserBadge(models.Model):
    """ A badge earned by an user for reading stories """

    badge_type = models.ForeignKey(
        BadgeType, verbose_name=_("Badge type"), 
        blank=False, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, verbose_name=_("User"), 
        blank=False, null=False, on_delete=models.CASCADE)
    offered_on = models.DateTimeField(
        verbose_name=_("Date offered"), auto_now_add=timezone.now, db_index=True)
    objects = models.Manager()
    visible = VisibleTypeManager()

    class Meta:
        ordering = ("-offered_on", )
        verbose_name = _("User badge")
        verbose_name_plural = _("User badges")
        unique_together = ("badge_type", "user")

    def __str__(self):
        return f"{self.badge_type} {self.user}"

    @staticmethod
    def create_badges_after_story(
            user: User, 
            org: Org, 
            category: Category
        ) -> List["UserBadge"]:
        """
        When an user has read a story, check if they should receive some badges
        """

        parent_category = CategoryExtras.get_parent_category(category)
        if parent_category:
            parent_subcategory_ids = CategoryExtras.get_subcategory_ids(parent_category)
        else:
            parent_subcategory_ids = []

        # Count how many stories the user has read
        total_reads = StoryRead.objects.filter(
            user=user, story__org=org).count()
        
        category_reads = StoryRead.objects.filter(
            user=user, story__category=category).count()

        if parent_category:
            subcategory_reads = StoryRead.objects.filter(
                user=user, story__category__in=[parent_category.pk]+parent_subcategory_ids).count()
        else:
            subcategory_reads = 0

        # Get the list of badges already earned by the current user
        current_badge_types = list(
            UserBadge.objects.filter(user=user).values_list("badge_type__id", flat=True))

        # Get new available badge types for no-category
        new_general_badge_types = BadgeType.visible.filter(
            org=org, validation_category=None, validation_total__lte=total_reads
        ).exclude(id__in=current_badge_types).all()

        # Get new available badge types for a specific (sub)category
        new_category_badge_types = BadgeType.visible.filter(
            validation_category=category, validation_total__lte=category_reads
        ).exclude(id__in=current_badge_types).all()

        # Get new available badge types for a parent category
        if parent_category:
            new_parent_badge_types = BadgeType.visible.filter(
                validation_category=parent_category, validation_total__lte=subcategory_reads
            ).exclude(id__in=current_badge_types).all()
        else:
            new_parent_badge_types = []

        # Create the badge offers
        creation_queue = []
        for badge_type in (
                list(new_general_badge_types) +
                list(new_category_badge_types) + 
                list(new_parent_badge_types)):
            badge = UserBadge(
                badge_type=badge_type,
                user=user,
                offered_on=timezone.now()
            )
            creation_queue.append(badge)
        
        # return all new badges    
        return UserBadge.objects.bulk_create(creation_queue)
    
