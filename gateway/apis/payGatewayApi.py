import requests
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, viewsets
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from gateway.apis.payGatewayDoc import base_pay_gateway_view__request_refund, base_pay_gateway_view__query_order, \
    base_pay_gateway_view__cancel_order, base_pay_gateway_view__create_order, base_pay_gateway_view__async_notify, \
    base_pay_gateway_view__sync_notify
from gateway.models import Billing
from gateway.models.gateway import PayGateway
from gateway.payutils.abstract import BaseTransactionResult
from gateway.serializers.payGatewaySz import PayGatewaySerializer, CreateOrderSerializer, RequestRefundSerializer, \
    QueryPlatformOrder, CancelPlatformOder


class TestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        data = {'id': validated_data.get('id'), 'name': validated_data.get('name')}
        return data


class BasePayGatewayView(viewsets.ReadOnlyModelViewSet):
    """
    签名方式：参数字典序排列，sign(拼接参数内容)
    """
    permission_classes = (permissions.AllowAny,)
    queryset = PayGateway.objects.all()
    serializer_class = PayGatewaySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []
    lookup_field = 'name'

    def get_queryset(self):
        return self.queryset.filter(enable=True)

    @extend_schema(**base_pay_gateway_view__create_order)
    @action(methods=['post'], detail=False, serializer_class=CreateOrderSerializer)
    def create_order(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,
                                           context={'request': request})
        print(request.META['HTTP_HOST'])
        if serializer.is_valid(True):
            data = serializer.save()
            print(data['url'])
            return Response({'detail': data})

    @extend_schema(**base_pay_gateway_view__request_refund)
    @action(methods=['post'], detail=False, serializer_class=RequestRefundSerializer)
    def request_refund(self, request, *args, **kwargs):
        """
        退款接口
        """
        serializer = RequestRefundSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save().data
            return Response({'detail': data})

    @extend_schema(**base_pay_gateway_view__cancel_order)
    @action(methods=['post'], detail=False, serializer_class=CancelPlatformOder)
    def cancel_order(self, request):
        """
        取消订单接口
        """
        serializer = CancelPlatformOder(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response({'detail': data})

    @extend_schema(**base_pay_gateway_view__query_order)
    @action(methods=['get'], detail=False, serializer_class=QueryPlatformOrder)
    def query_order(self, request, *args, **kwargs):
        """
        查询支付平台订单原始信息接口
        """
        data = {}
        _data = dict(request.query_params)
        for _key in _data:
            data[_key] = _data[_key][0]

        print(data)
        serializer = QueryPlatformOrder(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            return Response(data)

    @extend_schema(**base_pay_gateway_view__async_notify)
    @action(methods=['post'], detail=True)
    def async_notify(self, request, *args, **kwargs):
        """
        异步通知接口
        """
        pay = self.__get_pay()
        res = pay.notify_order(request)
        if res.status != res.SUCCESSFULLY_VERIFIED:
            print(f'验签失败：\n请求数据：{request.data}\n订单数据：{res}')
            return pay.failed_http()

        billing_m = Billing.objects.get(sid=res.sid)
        billing_m.pid = res.pid
        billing_m.status = billing_m.STATUS_PAID
        billing_m.save()

        data = {'sid': res.sid, 'name': billing_m.name, 'price': billing_m.price,
                'last_modify': billing_m.update_at, 'pid': res.pid, 'msg': 'null',
                'pay_status': 'successful'}
        sign = billing_m.app.to_sign_with_platform_private_key(data)
        data['sign'] = sign
        url = billing_m.app.notify_url
        merchant_res = requests.post(url, data=data)
        if 'ok' == merchant_res.text:
            self.__pay_success(res)
            print(f'商户已正确处理: {res}')
            return pay.success_http()
        else:
            print(f'商户未正确处理: {res}')
            return pay.failed_http()

    @extend_schema(**base_pay_gateway_view__sync_notify)
    @action(methods=['get'], detail=True)
    def sync_notify(self, request, *args, **kwargs):
        """
        同步通知接口，重定向应用设置的地址并携带已签名的参数
        """
        pay = self.__get_pay()
        data = dict(request.query_params)
        res: BaseTransactionResult = pay.return_order(data)
        billing_m = Billing.objects.get(sid=res.sid)

        data = {'sid': res.sid, 'name': billing_m.name, 'price': billing_m.price,
                'last_modify': billing_m.update_at, 'pid': res.pid, 'msg': 'null',
                'pay_status': 'unknown'}
        if res.status == res.SUCCESSFULLY_VERIFIED:
            billing_m.status = billing_m.STATUS_PAID
            billing_m.save()
            data['pay_status'] = 'successful'

        sign = billing_m.app.to_sign_with_platform_private_key(data)
        data['sign'] = sign
        url = billing_m.app.get_sync_notify_to_merchant_url(data)
        return redirect(url)

    def __get_pay(self):
        obj: PayGateway = self.get_object()
        return obj.get_pay_instance()

    @staticmethod
    def __pay_success(res: BaseTransactionResult):
        """
        @param res: BaseTransactionResult
        """
        return
