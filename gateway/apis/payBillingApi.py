from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from gateway.apis.payBillingDoc import base_pay_billing_view__query_order
from gateway.models import Billing
from gateway.serializers.payBillingSz import PayBillingSerializer, BasePayQueryBillingSerializer


class BasePayBillingView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Billing.objects.all()
    serializer_class = PayBillingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []

    @extend_schema(**base_pay_billing_view__query_order)
    @action(methods=['get'], permission_classes=[permissions.AllowAny],
            detail=False, serializer_class=BasePayQueryBillingSerializer)
    def query_order(self, request, *args, **kwargs):
        """
        查询订单接口，具体参数请查阅 swagger 接口
        """
        data = request.query_params
        serializer = BasePayQueryBillingSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            return Response(result.data)
