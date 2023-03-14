from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from ureport.userprofiles.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "rapidpro_uuid", 
            "image", 
        )


class UserWithProfileReadSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile")
        read_only_fields = fields

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


class CreateUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=128)

    class Meta:
        model = User
        fields = ("full_name", "email", "password")

    def validate_email(self, value):
        clean_email = value.strip()        
        if len(clean_email.split("@")) != 2:
            raise serializers.ValidationError(_("Wrong email format"))

        exists = User.objects.filter(username__iexact=clean_email).count()
        if exists:
            raise serializers.ValidationError(_("Email address already used"))
        else:
            return clean_email

    def create(self, validated_data):
        split_name = validated_data["full_name"].split(" ")
        
        first_name = split_name[0]
        if len(split_name) > 1:
            last_name = split_name[1]

        user = User(
            email=validated_data["email"],
            username=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    def validate(self, data):
        if not self.instance:
            raise serializers.ValidationError(_("User does not exist"))
        
        if not self.instance.check_password(data["current_password"]):
            raise serializers.ValidationError(_("Wrong current password"))

        if data["new_password"] != data["new_password2"]:
            raise serializers.ValidationError(_("The new passwords do not match"))
        
        return data

    def save(self):
        self.instance.set_password(self.validated_data["new_password"])
        self.instance.save()
        return self.instance


# class ForgotPasswordSerializer(serializers.Serializer):
#     # TODO:
#     # The .instance attribute will be the current User
#     user_id = serializers.IntegerField()
#     email = serializers.EmailField()
#     code = serializers.CharField()
#     new_password = serializers.CharField(max_length=128)
#     new_password2 = serializers.CharField(max_length=128)

#     def save(self):
#         pass