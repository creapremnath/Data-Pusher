# core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomTokenObtainPairView, PremOnlyAPIView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet, RoleViewSet, AccountViewSet,
    DestinationViewSet, LogViewSet, AccountMemberViewSet
)

# Setting up the DRF router for viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'account_member', AccountMemberViewSet)
router.register(r'destinations', DestinationViewSet)
router.register(r'logs', LogViewSet)

urlpatterns = [
    # Including all router-generated URLs (for CRUD on users, roles, etc.)
    path('', include(router.urls)),

    # Custom JWT token paths
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Custom login endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token endpoint

    # Custom API endpoint for premium users
    path('prem-only/', PremOnlyAPIView.as_view(), name='prem_only_api'),
]
