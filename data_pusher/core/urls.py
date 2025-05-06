# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import CustomTokenObtainPairView, PremOnlyAPIView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet, RoleViewSet, AccountViewSet,
    DestinationViewSet, LogViewSet, AccountMemberViewSet,
    SignupView,ProfileView
)

# Setting up the DRF router for viewsets
router = DefaultRouter()
# router.register(r'Sign-up', SignupView)
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'account_member', AccountMemberViewSet, basename='account_member')
router.register(r'destinations', DestinationViewSet)
router.register(r'logs', LogViewSet)

urlpatterns = [
    # Including all router-generated URLs (for CRUD on users, roles, etc.)
    path('sign-up/', SignupView.as_view(), name='sign-up'),

    # Custom JWT token paths
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Custom login endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token endpoint

    path('', include(router.urls)),

    # Custom API endpoint for premium users
    path('prem-only/', PremOnlyAPIView.as_view(), name='prem_only_api'),
    path('profile/', ProfileView.as_view(), name='profile_view'),
]
