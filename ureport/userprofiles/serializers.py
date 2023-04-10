from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ureport.userprofiles.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "full_name",
            "rapidpro_uuid", 
            "image", 
        )


class UserWithProfileReadSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    social_auth = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "social_auth", "username", "email", "first_name", "last_name", "profile")
        read_only_fields = fields

    def get_social_auth(self, user: User) -> bool:
        if not user.userprofile:
            return False
        return user.userprofile.is_social_auth()

    def to_representation(self, instance):
        """
        Move fields from UserProfile to User representation.
        Make sure that field names do not overlap!
        """
        representation = super().to_representation(instance)
        profile_representation = representation.pop('profile')
        if profile_representation:
            for key in profile_representation:
                representation[key] = profile_representation[key]
        return representation


class UserWithProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField()

    def save(self):
        if self.validated_data.get("full_name"):
            split_name = self.validated_data.get("full_name","").split(" ")
            self.instance.first_name = split_name[0]
            if len(split_name) > 1:
                self.instance.last_name = split_name[1]
            else:
                self.instance.last_name = ""

        self.instance.save()
        self.instance.userprofile.save()


class CreateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=128)
    rapidpro_uuid = serializers.CharField(max_length=36, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("full_name", "email", "password", "rapidpro_uuid")

    def validate_email(self, value: str) -> str:
        clean_email = value.strip()        
        if len(clean_email.split("@")) != 2:
            raise serializers.ValidationError(_("Wrong email format"))

        exists = User.objects.filter(username__iexact=clean_email).count()
        if exists:
            raise serializers.ValidationError(_("Email address already used"))
        else:
            return clean_email

    def create(self, validated_data: dict) -> User:
        split_name = validated_data.get("full_name","").split(" ")
        
        first_name = split_name[0]
        if len(split_name) > 1:
            last_name = split_name[1]
        else:
            last_name = ""

        user = User(
            email=validated_data.get("email"),
            username=validated_data.get("email"),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data.get("password"))
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.rapidpro_uuid = validated_data.get("rapidpro_uuid", "")
        profile.save()
        
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=False)
    new_password = serializers.CharField(max_length=128, required=False)
    new_password2 = serializers.CharField(max_length=128, required=False)

    def validate_email(self, value: str) -> str:
        clean_email = value.strip()        
        if len(clean_email.split("@")) != 2:
            raise serializers.ValidationError(_("Wrong email format"))
        return clean_email
    
    def validate(self, data: dict) -> dict:
        try:
            self.instance = User.objects.get(username__iexact=data.get("email"))
        except User.DoesNotExist:
            raise serializers.ValidationError(_("User does not exist"))

        if data.get("code") and data.get("code") != self.instance.userprofile.password_reset_code:
            raise serializers.ValidationError(_("Wrong code"))

        if data.get("new_password") != data.get("new_password2"):
            raise serializers.ValidationError(_("The new passwords do not match"))

        return data

    def save(self) -> User:
        if self.validated_data.get("code"):
            # We have a validated code
            if self.validated_data.get("new_password"):
                # and a new password has been provided
                self.instance.set_password(self.validated_data.get("new_password"))
                self.instance.save()
                self.instance.userprofile.password_reset_code = ""
                self.instance.userprofile.save()
            else:
                self.instance.userprofile.increment_reset_retries()
                self.instance.userprofile.save()
        else:
            # The frontend only provided the email address
            self.instance.userprofile.generate_reset_code()
            print("CODE = ", self.instance.userprofile.password_reset_code)
            send_mail(
                _("Password reset code"),
                _("Your password reset code is: {}".format(self.instance.userprofile.password_reset_code)),
                settings.DEFAULT_FROM_EMAIL,
                [self.instance.email],
                fail_silently=False,
            )
        return self.instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, data: dict) -> dict:
        if not self.instance:
            raise serializers.ValidationError(_("User does not exist"))
        
        if not self.instance.check_password(data["current_password"]):
            raise serializers.ValidationError(_("Wrong current password"))

        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(_("The new passwords do not match"))
        
        return data

    def save(self) -> User:
        self.instance.set_password(self.validated_data["new_password"])
        self.instance.save()
        return self.instance
