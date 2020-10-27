from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from gateway.models import PayApplication
from gateway.serializers.payApplicationSz import PayApplicationSerializer


class BasePayApplicationView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    queryset = PayApplication.objects.all()
    serializer_class = PayApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []
    lookup_field = 'app_id'

    @action(methods=['get'], detail=True)
    def get_public_key(self, request, *args, **kwargs):
        """
        获取应用公钥
        """
        app: PayApplication = self.get_object()
        key = app.get_platform_public_key()
        return Response({'detail': key})
