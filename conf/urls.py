"""OnePay URL Configuration

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
from drf_spectacular.views import SpectacularRedocView, SpectacularSwaggerView, SpectacularAPIView
from rest_framework.routers import DefaultRouter

from gateway.apis.payApplicationApi import BasePayApplicationView
from gateway.apis.payBillingApi import BasePayBillingView
from gateway.apis.payGatewayApi import BasePayGatewayView

router = DefaultRouter()
router.register(r'PayGateway/BaseGateway', BasePayGatewayView)
router.register(r'PayGateway/BaseApplication', BasePayApplicationView)
router.register(r'PayGateway/BaseBilling', BasePayBillingView)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'api/', include(router.urls)),
    url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),
    path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('docs/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += [
        path('api-auth/', include('rest_framework.urls')),
        path('__debug__/', include(debug_toolbar.urls)),
    ]
