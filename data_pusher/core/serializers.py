from rest_framework import serializers
from .models import User, Role, Account, Destination, Log, AccountMember
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.db import transaction


# Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',        # included but write-only
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        extra_kwargs = {
            'created_by': {'required': False},
            'updated_by': {'required': False},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


# Account Serializer
class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = "__all__"


# Destination Serializer
class DestinationSerializer(serializers.ModelSerializer):
    account_id = serializers.SlugRelatedField(slug_field='account_name', queryset=Account.objects.all())
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Destination
        fields = [
            'destination_id', 'account_id', 'url', 'http_method', 'headers',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


# Log Serializer
class LogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Log
        fields = [
            'event_id', 'account_id', 'destination_id', 'received_timestamp',
            'processed_timestamp', 'received_data', 'status'
        ]







#Working one
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)

#         # Add custom claims
#         token['username'] = user.username
#         token['email'] = user.email
#         # You can add more custom claims based on your user model or other data
#         # Example:
#         token['is_staff'] = user.is_staff
#         token['groups'] = [group.name for group in user.groups.all()]

#         return token


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Basic user info
        token['user_id'] = user.id
        # token['email'] = user.email
        # token['is_staff'] = user.is_staff
        # token['groups'] = [group.name for group in user.groups.all()]

        # Add organization and role info
        try:
            membership = AccountMember.objects.get(user_id=user)
            token['account_id'] = str(membership.account_id.account_id)
            token['role_id'] = membership.role_id.role_id if membership.role_id else None
        except AccountMember.DoesNotExist:
            token['account_id'] = None
            token['role_id'] = None

        return token




    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Optionally add the custom claims to the response payload
        # data['username'] = self.user.username
        # data['email'] = self.user.email
        # Example:
        # data['is_staff'] = self.user.is_staff
        # data['groups'] = [group.name for group in self.user.groups.all()]
        return data



from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import Account, User, Role, AccountMember

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import Account, User, Role, AccountMember

# class SignupSerializer(serializers.Serializer):
#     # Account info
#     account_name = serializers.CharField(required=True)
#     website = serializers.URLField(required=False, allow_blank=True)

#     # User info
#     username = serializers.CharField(required=True)
#     email = serializers.EmailField(required=True)
#     password = serializers.CharField(write_only=True, required=True)

#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("A user with this email already exists.")
#         return value

#     @transaction.atomic
#     def create(self, validated_data):
#         # Default role_id to 1
#         try:
#             role = Role.objects.get(pk=1)
#         except Role.DoesNotExist:
#             raise serializers.ValidationError("Default role (id=1) does not exist.")

#         # Create Account
#         account = Account.objects.create(
#             account_name=validated_data['account_name'],
#             website=validated_data.get('website', ''),
#             created_by='',
#             updated_by='',
#         )

#         # Create User
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=make_password(validated_data['password']),
#             created_by='',
#             updated_by='',
#         )

#         # Create AccountMember
#         AccountMember.objects.create(
#             account_id=account,
#             user_id=user,
#             role_id=role,
#             created_by='',
#             updated_by='',
#         )

#         return {
#             'account_id': account.account_id,
#             'account_name': account.account_name,
#             'user_id': user.id,
#             'email': user.email,
#             'role_id': role.role_id,
#         }




# Account Member Serializer

class AccountMemberSerializer(serializers.ModelSerializer):
    # Read-only display fields
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    # ForeignKey input fields (for writes)
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, allow_null=True)

    class Meta:
        model = AccountMember
        fields = [
            'account', 'account_name',
            'user', 'user_email',
            'role', 'role_name',
            'created_at', 'updated_at',
            'created_by', 'updated_by',
        ]
        read_only_fields = ['created_at', 'updated_at', 'account_name', 'user_email', 'role_name']

    def create(self, validated_data):
        # Handle creation logic if you need to customize how it's created
        account_member = AccountMember.objects.create(**validated_data)
        return account_member


class OrgMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountMember
        fields = "__all__"



def validate_unique_email(value):
    User = get_user_model()
    if User.objects.filter(email=value).exists():
        raise serializers.ValidationError("A user with this email already exists.")
    return value

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(validators=[validate_unique_email])
    password = serializers.CharField(write_only=True)
    account_name = serializers.CharField()
    website = serializers.URLField(required=False, allow_blank=True)

    @transaction.atomic
    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        website = validated_data.get('website')
        account_name = validated_data['account_name']

        role = Role.objects.get(pk=1)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            created_by='self',  # optional depending on your model
        )

        # Create account
        account = Account.objects.create(
            account_name=account_name,
            website=website,
            created_by=user
        )

        # Create Account Member
        account_member = AccountMember.objects.create(
            account_id=account,
            user_id=user,
            role_id=role,
            created_by=user
        )

        return {
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': role.role_id,
            'account_id': str(account),
            'account_name': account.account_name,
            'website': account.website
        }


class MemberManagerSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    account_id = serializers.CharField()
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.filter(pk__in=[1, 2]))


    @transaction.atomic
    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        account_id = validated_data['account_name']
        role_id = validated_data['role_id']
        created_by = validated_data['created_by']
        created_at = validated_data['created_at']
        updated_by = validated_data['updated_by']
        updated_at = validated_data['updated_at']


        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            created_by=created_by,
            created_at=created_at,
            updated_by=updated_by,
            updated_at=updated_at
        )

        # Create Account Member
        account_member = AccountMember.objects.create(
            account_id=account_id,
            user_id=user,
            role_id=role_id,
            created_by=user
        )

        return {
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': role_id,
            'account_id':account_id,
            'created_by':created_by,
            'created_at':created_at,
            'updated_by':updated_by,
            'updated_at':updated_at

        }
