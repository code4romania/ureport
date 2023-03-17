from datetime import timedelta
from random import randint
from functools import partial

from dash.utils import generate_file_path
from django.db import models, IntegrityError
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserProfile(models.Model):
    """
    This class links an Ureport user account to a RapidPro contact
    based on the RapidPro UUID.
    """

    user = models.OneToOneField(
        User, verbose_name=_("User"), blank=False, null=False, on_delete=models.CASCADE,
        primary_key=True)
    
    # We do not use a ForeignKey because there can be several "Contacts" with
    # the same imported UUID but assigned to different Orgs
    rapidpro_uuid = models.CharField(
        verbose_name=_("RapidPro Contact UUID"), 
        max_length=36, blank=True, null=False, default="", db_index=True)

    image = models.ImageField(
        verbose_name=_("Image"), 
        upload_to=partial(generate_file_path, "userprofiles"),
        blank=True, null=True,
        help_text=_("The profile image file to use"))

    points = models.PositiveIntegerField(
        verbose_name=_("Points"),
        default=0, blank=True, null=False, editable=False,
        help_text=_("Cached computed total points"))

    password_reset_code = models.CharField(
        verbose_name=_("Confirmation code"), 
        max_length=8, blank=True, null=False, default="", editable=False,
        help_text=_("Confirmation code for the password reset"))

    password_reset_expiry = models.DateTimeField(
        verbose_name=_("Expiration date"), blank=True, null=True, editable=False,
        help_text=_("Expiration date for the password reset code"))

    password_reset_retries = models.PositiveSmallIntegerField(
        verbose_name=_("Confirmation code retries"), 
        default=0, blank=True, null=False, editable=False,
        help_text=_("How many attempts were made for this confirmation code"))

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("Use profiles")

    def generate_reset_code(self):
        self.password_reset_code = "{}".format(randint(1000, 9999))
        self.password_reset_retries = 0
        self.password_reset_expiry = timezone.now() + timedelta(hours=6)
        self.save()

    def increment_reset_retries(self):
        self.password_reset_retries += 1
        self.save()

    def validate_reset_code(self, input):
        if timezone.now() > self.password_reset_expiry:
            return False
        if input != self.password_reset_code:
            return False
        return True

    @property
    def full_name(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)


@receiver(post_save, sender=User)
def auto_create_user_profile(sender, instance, **kwargs):
    if not UserProfile.objects.filter(user=instance).exists():
        try:
            UserProfile.objects.create(user=instance)
        except IntegrityError:
            pass
