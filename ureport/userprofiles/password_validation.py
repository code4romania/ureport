import string
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class OneOfEachPasswordValidator:
    def __init__(self):
        pass

    def validate(self, password: str, user: User=None):
        has_lowercase = False
        has_uppercase = False
        has_punctuation = False
        has_digit = False

        for c in password:
            if c.islower():
                has_lowercase = True
            elif c.isupper():
                has_uppercase = True
            elif c.isdigit():
                has_digit = True
            elif c in string.punctuation:
                has_punctuation = True

        if not has_punctuation or not has_digit or not has_lowercase or not has_uppercase:
            raise ValidationError(
                _(
                    "The password does not contain at least one number, one punctuation character,"
                    " one uppercase letter, and one lowercase letter."
                ),
                code='password_no_different_char_types',
            )

    def get_help_text(self):
        return _(
            "The password must contain at least one number, one punctuation character,"
            " one uppercase letter, and one lowercase letter."
        )


class DifferentPasswordValidator:
    def __init__(self):
        pass

    def validate(self, password: str, user: User=None):
        if not user:
            return
        
        if user.check_password(password):
            raise ValidationError(
                _("The new password is identical with the current password"),
                code='password_identical',
            )

    def get_help_text(self):
        return _("The new password must not be identical with the current password"),
