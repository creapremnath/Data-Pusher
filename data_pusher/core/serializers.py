from rest_framework import serializers
from .models import User, Role, Account, Destination, Log, AccountMember
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


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
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Account
        fields = [
            'account_id', 'account_name', 'app_secret_token',
            'website', 'created_at', 'updated_at',
            'created_by', 'updated_by'
        ]


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


class AccountMemberSerializer(serializers.ModelSerializer):
    # You can use the `related_name` to refer to the related model field.
    account_name = serializers.CharField(source='account_id.account_name', read_only=True)
    user_email = serializers.EmailField(source='user_id.email', read_only=True)
    role_name = serializers.CharField(source='role_id.role_name', read_only=True)

    # ForeignKey fields can be represented by their IDs or by nested serializers.
    account_id = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False, allow_null=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.CharField(max_length=255, required=False, allow_blank=True)
    updated_by = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = AccountMember
        fields = ['account_id', 'account_name', 'user_id', 'user_email', 'role_id', 'role_name',
                  'created_at', 'updated_at', 'created_by', 'updated_by']
        extra_kwargs = {
            'account_id': {'required': True},
            'user_id': {'required': True},
            'role_id': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        # Handle creation logic if you need to customize how it's created
        account_member = AccountMember.objects.create(**validated_data)
        return account_member






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
        token['username'] = user.username
        token['email'] = user.email
        # token['is_staff'] = user.is_staff
        # token['groups'] = [group.name for group in user.groups.all()]

        # Add organization and role info
        try:
            membership = AccountMember.objects.get(user_id=user)
            token['org_id'] = str(membership.account_id.account_id)
            token['role'] = membership.role_id.role_name if membership.role_id else None
        except AccountMember.DoesNotExist:
            token['org_id'] = None
            token['role'] = None

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