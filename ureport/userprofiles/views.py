from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import decorators
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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


@decorators.api_view(["POST"])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = Token.objects.get_or_create(user=user)[0]
    return Response({
        "id": user.id,
        "token": token.key,
    })


@decorators.api_view(["POST"])
@decorators.permission_classes([IsOwnerUserOrAdmin])
def change_password(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise Http404

    serializer = ChangePasswordSerializer(instance=user, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({})


class UserViewSet(ModelViewSet):
    """
    """
    
    serializer_class = UserWithProfileReadSerializer
    queryset = User.objects.all()
    model = User

    def get_permission(self):
        if self.action == "retrieve_current_user_with_profile":
            return [IsAuthenticated()]
        return [IsOwnerUserOrAdmin()]

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
