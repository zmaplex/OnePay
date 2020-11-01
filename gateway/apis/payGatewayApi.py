import requests
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, viewsets
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from gateway.apis.payGatewayDoc import base_pay_gateway_view__request_refund
from gateway.models import Billing
from gateway.models.gateway import PayGateway
from gateway.payutils.abstract import BaseTransactionResult
from gateway.payutils.pay import Pay
from gateway.serializers.payGatewaySz import PayGatewaySerializer, CreateOrderSerializer, RequestRefundSerializer


class TestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        data = {'id': validated_data.get('id'), 'name': validated_data.get('name')}
        return data


class BasePayGatewayView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = PayGateway.objects.all()
    serializer_class = PayGatewaySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = []
    lookup_field = 'name'

    def get_queryset(self):
        return self.queryset.filter(enable=True)

    @action(methods=['post'], detail=False, serializer_class=CreateOrderSerializer)
    def create_order(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,
                                           context={'request': request})
        print(request.META['HTTP_HOST'])
        if serializer.is_valid(True):
            data = serializer.save()
            print(data['url'])
            return Response({'detail': data})

    @swagger_auto_schema(**base_pay_gateway_view__request_refund)
    @action(methods=['post'], detail=False, serializer_class=RequestRefundSerializer)
    def request_refund(self, request, *args, **kwargs):
        """
        退款接口
        """
        serializers = RequestRefundSerializer(data=request.data)
        if serializers.is_valid(raise_exception=True):
            data = serializers.save().data
            return Response({'detail': data})

    def cancel_order(self):
        """
        取消订单接口
        """

    def query_order(self):
        """
        查询订单接口
        """

    @action(methods=['post'], detail=True)
    def async_notify(self, request, *args, **kwargs):
        """
        异步通知接口
        发送 form 数据格式 ：
        {'sid': 本系统的账单ID, 'name': 账单名字, 'price': 价格,
                'last_modify': 最后修改时间, 'pid': 平台账单ID,
                'msg': 'null','pay_status': 'successful'}
        """
        print(f'收到异步通知数据：{request.data}')
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
        print('商户数据')
        print(merchant_res.text)
        if 'ok' == merchant_res.text:
            self.__pay_success(res)
            print(f'商户已正确处理: {res}')
            return pay.success_http()
        else:
            print(f'商户未正确处理: {res}')
            return HttpResponse('商户未正确处理')

    @action(methods=['get'], detail=True)
    def sync_notify(self, request, *args, **kwargs):
        """
        同步通知接口，重定向应用设置的地址并携带已签名的参数
        """
        pay = self.__get_pay()
        data = dict(request.query_params)
        res = pay.return_order(data)
        billing_m = Billing.objects.get(sid=res.sid)
        data = {
            'sid': res.sid,
            'name': billing_m.name,
            'price': billing_m.price,
            'last_modify': billing_m.update_at,
            'msg': 'null'
        }
        sign = billing_m.app.to_sign_with_platform_private_key(data)
        data['sign'] = sign
        url = billing_m.app.get_sync_notify_to_merchant_url(data)
        return redirect(url)

    def __get_pay(self):
        obj = self.get_object()
        config = obj.pay_config
        return Pay.get_instance(obj.name, config)

    @staticmethod
    def __pay_success(res: BaseTransactionResult):
        """
        @param res: BaseTransactionResult
        """
        return
