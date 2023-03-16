from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import decorators
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ureport.apiextras.views import (
    IsOwnerUserOrAdmin,
    USER_API_PATH,
    CURRENT_USER_API_PATH,
)
from ureport.userprofiles.serializers import (
    UserWithProfileReadSerializer,
    UserProfileSerializer, 
    CreateUserSerializer,
    ChangePasswordSerializer,
)



class UserViewSet(GenericViewSet):
    """
    """
    
    serializer_class = UserWithProfileReadSerializer
    queryset = User.objects.all()
    # model = User

    def get_permission(self):
        if self.action == "retrieve_current_user_with_profile":
            return [IsAuthenticated()]
        elif self.action == "create_user":
            return []
        return [IsOwnerUserOrAdmin()]

    # @decorators.api_view(["POST"])
    @decorators.action(detail=False, methods=['post'])
    def create_user(request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get_or_create(user=user)[0]
        return Response({
            "id": user.id,
            "token": token.key,
        })

    # @decorators.api_view(["POST"])
    # @decorators.permission_classes([IsOwnerUserOrAdmin])
    @decorators.action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def change_password(request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404

        serializer = ChangePasswordSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({})

    @decorators.action(detail=False, methods=['get'], url_path=CURRENT_USER_API_PATH)
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
        queryset = self.get_queryset().filter(id=user_id).get()
        serializer = UserWithProfileReadSerializer(queryset, many=False)
        return Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], url_path=USER_API_PATH)
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
        queryset = self.get_queryset().filter(id=user_id).get()
        serializer = UserWithProfileReadSerializer(queryset, many=False)
        return Response(serializer.data)
