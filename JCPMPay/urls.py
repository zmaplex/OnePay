"""JCPMPay URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

from gateway.apis.PayApplicationApi import BasePayApplicationView
from gateway.apis.payGatewayApi import BasePayGatewayView

router = DefaultRouter()
router.register(r'PayGateway/PayGateway', BasePayGatewayView)
router.register(r'PayGateway/PayApplication', BasePayApplicationView)

if settings.DEBUG:
    doc_permissions = permissions.AllowAny
else:
    doc_permissions = permissions.IsAdminUser

schema_view = get_schema_view(
    openapi.Info(
        title="API接口文档平台",
        default_version='v1',
        description="JCPMDOCS",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="nesnode@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(doc_permissions,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='文档')),
    url(r'api/', include(router.urls)),
    url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += [
        path('api-auth/', include('rest_framework.urls')),
        path('__debug__/', include(debug_toolbar.urls)),
    ]