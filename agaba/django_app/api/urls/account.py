from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView

from ..views import account as account_views

router = DefaultRouter()
router.register(
    r'companies', account_views.CompanyViewSet, 
    basename='company'
)
router.register(
    r'search_company', account_views.SearchCompanyViewSet, 
    basename='search-company'
)
router.register(
    r'users', account_views.CustomUserViewSet, 
    basename='user'
)

urlpatterns = [
    path(
        'users/me/avatar/', account_views.AvatarUpdateView.as_view(), 
        name='user-avatar-update'
    ),
    path(
        'auth/jwt/refresh/', SimpleJWTTokenRefreshView.as_view(), 
        name='token_refresh'
    ),
]
