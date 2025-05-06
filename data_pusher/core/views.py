# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import User, Role, Account, Destination, Log, AccountMember
from .serializers import (
    UserSerializer, RoleSerializer, AccountSerializer,
    DestinationSerializer, LogSerializer, AccountMemberSerializer,
    SignupSerializer,
)

from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

#####################
#JWT
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins, generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin, IsAuthenticatedViaJWT
from .serializers import CustomTokenObtainPairSerializer
####################


###SwaggerUI configuration

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

# @extend_schema_view(
#     list=extend_schema(
#         parameters=[
#             OpenApiParameter(
#                 'tags',
#                 OpenApiTypes.STR,
#                 description='Comma separated list of tag IDs to filter',
#             ),
#             OpenApiParameter(
#                 'ingredients',
#                 OpenApiTypes.STR,
#                 description='Comma separated list of ingredient IDs to filter',
#             ),
#         ]
#     )
# )

#############



class SignupView(APIView):

    @extend_schema(
        request=SignupSerializer,  # Request body schema
        responses={201: SignupSerializer},  # Response schema for success
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()  # Perform create action (e.g., user registration)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignupView(API):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()  # Perform create action (e.g., user registration)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomTokenObtainPairView(APIView):
    permission_classes = ()
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)



class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RoleViewSet(viewsets.ModelViewSet,):
    permission_classes = [IsAuthenticated,IsAuthenticatedViaJWT]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

##################################

class AccountMemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthenticatedViaJWT]  # Ensure the user is authenticated with JWT
    serializer_class = AccountMemberSerializer

    def get_queryset(self):
        """
        Override the default queryset method to filter by account_id from the JWT token
        and apply role-based permissions.
        """
        # Extract user and JWT payload
        user = self.request.user  # User authenticated in JWT
        jwt_payload = getattr(self.request, 'jwt_payload', None)  # Assuming jwt_payload is available in the request

        if jwt_payload is None:
            raise PermissionDenied('JWT payload is missing.')

        # Extract account_id and role_id from the JWT payload
        account_id = jwt_payload.get('account_id')
        role_id = jwt_payload.get('role_id')

        if account_id is None:
            raise PermissionDenied('Account ID is missing in the JWT token.')

        # If role_id is None, it indicates invalid permission data
        if role_id is None:
            raise PermissionDenied('Role ID is missing in the JWT token.')

        # For Admin (role_id = 1), allow full CRUD on AccountMembers where account_id matches the JWT account_id
        if role_id == 1:
            # Admin can access all CRUD operations, filtered by account_id
            return AccountMember.objects.filter(account_id=account_id)

        # For Normal User (role_id = 2), allow only read access (GET) to their own account's data
        elif role_id == 2:
            # Normal users can only read data related to their account_id
            if self.action == 'list' or self.action == 'retrieve':
                return AccountMember.objects.filter(account_id=account_id)
            else:
                raise PermissionDenied("You do not have permission to modify this data.")

        # If role_id is neither 1 nor 2, deny access
        else:
            raise PermissionDenied('You do not have the necessary role permissions.')

###########################

class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer




class PremOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get(self, request, *args, **kwargs):
        return Response({"message": "This API is accessible only to user 'prem'."}, status=status.HTTP_200_OK)

from core.permissions import IsAuthenticatedViaJWT

class ProfileView(APIView):
    permission_classes = [IsAuthenticatedViaJWT]  # ✅ Enforce JWT-based access

    def get(self, request):
        user = request.user  # ✅ already set from permission class

        return Response({
            "user_id": user.id,
            "account_id": request.jwt_payload.get('account_id')
  # Customize this field based on your model
        })