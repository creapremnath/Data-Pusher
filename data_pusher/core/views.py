# from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import User, Role, Account, Destination, Log, AccountMember
from .serializers import (
    UserSerializer, RoleSerializer, AccountSerializer,
    DestinationSerializer, LogSerializer, AccountMemberSerializer
)


#####################
#JWT
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPremUser
from .serializers import CustomTokenObtainPairSerializer
####################

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class AccountMemberViewSet(viewsets.ModelViewSet):
    queryset = AccountMember.objects.all()
    serializer_class = AccountMemberSerializer



class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer




class CustomTokenObtainPairView(APIView):
    permission_classes = ()
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class PremOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsPremUser]

    def get(self, request, *args, **kwargs):
        return Response({"message": "This API is accessible only to user 'prem'."}, status=status.HTTP_200_OK)