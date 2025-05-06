# yourapp/permissions.py
from rest_framework import permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class IsAdmin(permissions.BasePermission):
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


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

# def get_current_user(request):
#     """
#     Extracts and verifies user from JWT token in the request.
#     Returns only the authenticated user instance.
#     """
#     try:
#         user = JWTAuthentication().authenticate(request)
#         if user is not None:
#             payload = user[1]

#             return payload
#         else:
#             raise AuthenticationFailed('Authentication credentials were not provided.')
#     except Exception as e:
#         raise AuthenticationFailed(f'Invalid or missing token: {str(e)}')


class IsAuthenticatedViaJWT(permissions.BasePermission):
    """
    Custom permission that authenticates via JWT and attaches payload to request.
    """

    def has_permission(self, request, view):
        try:
            user_auth_tuple = JWTAuthentication().authenticate(request)
            if user_auth_tuple is not None:
                user, validated_token = user_auth_tuple
                request.user = user
                request.jwt_payload = validated_token  # Attach token payload to request
                return True
            else:
                raise AuthenticationFailed('Authentication credentials were not provided.')
        except Exception as e:
            raise AuthenticationFailed(f'Invalid or missing token: {str(e)}')