from django.contrib.auth.models import User
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from rest_framework import decorators
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ureport.apiextras.views import (
    IsOwnerUserOrAdmin,
    SerializerErrorResponse,
    USER_API_PATH,
    CURRENT_USER_API_PATH,
)
from ureport.userprofiles.models import UserProfile
from ureport.userprofiles.serializers import (
    UserWithProfileReadSerializer,
    UserWithProfileSerializer, 
    CreateUserSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)


class CustomAuthToken(ObtainAuthToken):

    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data.get('user')
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "id": user.pk,
                "token": token.key,
            })
        else:
            return SerializerErrorResponse(serializer.errors)


class UserProfileViewSet(GenericViewSet):
    """
    """
    
    queryset = User.objects.all()
    model = UserProfile

    def get_serializer_class(self):
        # TODO: Replace hardcoded serializers in actions
        if self.action == "reset_password":
            return ResetPasswordSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        elif self.action == "create_user":
            return CreateUserSerializer
        else:
            return UserWithProfileReadSerializer

    def get_permissions(self):
        if self.action == "retrieve_current_user_with_profile":
            return [IsAuthenticated()]
        elif self.action in ("create_user", "reset_password"):
            return []
        return [IsOwnerUserOrAdmin()]

    def partial_update(self, request, user_id):
        # TODO:
        pass

    @decorators.action(detail=False, methods=('post',))
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OK"})
        else:
            return SerializerErrorResponse(serializer.errors)

    @decorators.action(detail=False, methods=('post',))
    def create_user(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get_or_create(user=user)[0]
            return Response({
                "id": user.id,
                "token": token.key,
            })
        else:
            return SerializerErrorResponse(serializer.errors)

    @decorators.action(detail=False, methods=('post',), url_path=USER_API_PATH)
    def change_password(self, request, user_id):
        try:
            user = self.get_queryset().get(pk=user_id)
        except User.DoesNotExist:
            return SerializerErrorResponse("User does not exist")

        serializer = ChangePasswordSerializer(instance=user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OK"})
        else:
            return SerializerErrorResponse(serializer.errors)

    @decorators.action(detail=False, methods=('get',), url_path=CURRENT_USER_API_PATH)
    @method_decorator(vary_on_headers("Authorization",))
    def retrieve_current_user_with_profile(self, request):
        """
        Retrieve the current User and their UserProfile

        Example:
            
            GET /api/v1/userprofiles/user/@me/

        Response will contain both the User and UserProfile as a flat dict

            {
                "id": 3,
                "username": "string",
                "email": "email",
                "first_name": "string",
                "last_name": "string",
                "rapidpro_uuid": "string",
                "image": "string" | null
            }
        """
        user_id = request.user.id
        try:
            queryset = self.get_queryset().get(pk=user_id)
        except User.DoesNotExist:
            raise Http404
        serializer = UserWithProfileReadSerializer(queryset, many=False)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=('get',), url_path=USER_API_PATH)
    def retrieve_user_with_profile(self, request, user_id):
        """
        Retrieve the User and their UserProfile

        Example:
            
            GET /api/v1/userprofiles/user/3/

        Response will contain both the User and UserProfile as a flat dict

            {
                "id": 3,
                "username": "string",
                "email": "email",
                "first_name": "string",
                "last_name": "string",
                "rapidpro_uuid": "string",
                "image": "string" | null
            }
        """

        try:
            queryset = self.get_queryset().get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        serializer = UserWithProfileReadSerializer(queryset, many=False)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=('delete',), url_path=USER_API_PATH)
    def delete_user(self, request, user_id):
        """
        Delete the User and their UserProfile

        Example:
            
            DELETE /api/v1/userprofiles/user/3/

        Response will contain the operation status

            {
                "detail": "OK"
            }
        """

        try:
            queryset = self.get_queryset().get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        if queryset.is_staff:
            return SerializerErrorResponse(_("Cannot delete an admin account"))
        else:
            queryset.delete()
            return Response({"detail": "OK"})
