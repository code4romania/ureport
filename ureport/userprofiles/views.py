from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import decorators, status
from rest_framework.authtoken.views import ObtainAuthToken
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
    ResetPasswordSerializer,
)

class SerializerErrorResponse(Response):

    def __init__(self, data=""):
        if type(data) is str:
            output = {
                "detail": data,
                "errors": data,
            }
        else:
            output = {
                "detail": data[list(data)[0]][0],  # The text of an error message from a dict of error messages
                "errors": data,
            }
        return super().__init__(output, status=status.HTTP_400_BAD_REQUEST)
   


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
            })
        else:
            return SerializerErrorResponse(serializer.errors)


class UserViewSet(GenericViewSet):
    """
    """
    
    serializer_class = UserWithProfileReadSerializer
    queryset = User.objects.all()
    # model = User

    def get_permission(self):
        if self.action == "retrieve_current_user_with_profile":
            return [IsAuthenticated()]
        elif self.action in ("create_user", "forgot_initial", "forgot_check", "forgot_change"):
            return []
        return [IsOwnerUserOrAdmin()]

    @decorators.action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OK"})
        else:
            return SerializerErrorResponse(serializer.errors)

    @decorators.action(detail=False, methods=['post'])
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

    @decorators.action(detail=False, methods=['post'], url_path=USER_API_PATH)
    def change_password(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return SerializerErrorResponse("User does not exist")

        serializer = ChangePasswordSerializer(instance=user, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OK"})
        else:
            return SerializerErrorResponse(serializer.errors)

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
        try:
            queryset = self.get_queryset().filter(id=user_id).get()
        except User.DoesNotExist:
            raise Http404
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
