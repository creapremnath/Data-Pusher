# yourapp/permissions.py
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication

class IsADMIN(permissions.BasePermission):
    """
    Allows access only to users with the username 'prem' in their JWT.
    """

    def has_permission(self, request, view):
        try:
            user = JWTAuthentication().authenticate(request)
            if user is not None:
                payload = user[1]
                print(payload.get('admin'))# The second element is the decoded payload
                return payload.get('role').upper() == 'ADMIN'
            return False
        except Exception:
            return False