from rest_framework import serializers
from .models import User, Role, Account, Destination, Log

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at', 'updated_at', 'created_by', 'updated_by']


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


class DestinationSerializer(serializers.ModelSerializer):
    account = serializers.SlugRelatedField(slug_field='account_name', queryset=Account.objects.all())
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Destination
        fields = [
            'id', 'account', 'url', 'http_method', 'headers',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]


class LogSerializer(serializers.ModelSerializer):
    account = serializers.SlugRelatedField(slug_field='account_name', read_only=True)
    destination = DestinationSerializer(read_only=True)

    class Meta:
        model = Log
        fields = [
            'event_id', 'account', 'destination', 'received_timestamp',
            'processed_timestamp', 'received_data', 'status'
        ]
