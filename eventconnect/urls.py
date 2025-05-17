# project/urls.py

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Event Connect",
        default_version='v1',
        description="API documentation for Event Connect",
        terms_of_service="http://localhost:8000/",
        contact=openapi.Contact(email="mdzoubir012@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # --- JWT endpoints ---
    path('api/auth/token/',         TokenObtainPairView.as_view(),  name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),
    path('api/auth/token/verify/',  TokenVerifyView.as_view(),     name='token_verify'),


    # --- API documentation ---
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('',   schema_view.with_ui('swagger', cache_timeout=0),   name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # --- app’s endpoints ---
    path('api/', include('events.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
