from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .urls import account as account_urls
from .urls import balance as balance_urls
from .urls import products as products_urls
from .urls import orders as orders_urls
from .urls import messenger as messenger_urls

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="API для платформы AGABA",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.registry.extend(account_urls.router.registry)
router.registry.extend(balance_urls.router.registry)
router.registry.extend(products_urls.router.registry)
router.registry.extend(orders_urls.router.registry)

urlpatterns = [
    path('', include(router.urls)),
    *account_urls.urlpatterns,
    *balance_urls.urlpatterns,
    *products_urls.urlpatterns,
    *orders_urls.urlpatterns,
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    *messenger_urls.urlpatterns,
]
