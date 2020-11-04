from decimal import Decimal

from django.conf import settings
from rest_framework import serializers

from gateway.models import PayGateway, PayApplication, Billing
from gateway.payutils.abstract import BaseTransactionSlip, BaseRequestRefund, BaseOrderId
from gateway.serializers.baseSz import BaseSz
from gateway.serializers.payBillingSz import PayBillingSerializer


class PayGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayGateway
        fields = ['id', 'name', 'alias_name', 'enable', 'description']


class BasePlatformOder(BaseSz):
    sid = serializers.CharField(max_length=20, label="订单号", help_text="为本系统的订单号")

    def validate(self, attrs):
        data = dict(attrs)
        self.verify_signature(data)
        sid = data.get('sid')
        billing_m = Billing.objects.filter(sid=sid)
        if not billing_m.exists():
            raise serializers.ValidationError('查询的订单不存在')
        return attrs


class CancelPlatformOder(BasePlatformOder):
    def create(self, data):
        sid = data.get('sid')
        billing_m = Billing.objects.get(sid=sid)
        gateway = billing_m.gateway.get_pay_instance()
        res = gateway.cancel_order(BaseOrderId(sid=sid, pid=billing_m.pid))
        data = {'status': res.status, 'platform_detail': res.detail}
        return data


class QueryPlatformOrder(BasePlatformOder):

    def create(self, data):
        sid = data.get('sid')
        billing_m = Billing.objects.get(sid=sid)
        gateway = billing_m.gateway.get_pay_instance()
        return gateway.query_order(BaseOrderId(sid=sid, pid=billing_m.pid))

    def validate(self, attrs):
        return super(QueryPlatformOrder, self).validate(attrs)


class RequestRefundSerializer(BaseSz):
    sid = serializers.CharField(max_length=20, label="订单号", help_text="为本系统的订单号")
    price = serializers.CharField(max_length=20, label="退款费用", help_text="不能高于订单金额")

    def create(self, data):
        sid = data.get('sid')
        price = data.get('price')
        billing_m = Billing.objects.get(sid=sid)
        if billing_m.status == billing_m.STATUS_PAID:
            pay = billing_m.gateway.get_pay_instance()
            res = pay.request_refund(BaseRequestRefund(sid, billing_m.pid, price))
            if res:
                billing_m.status = billing_m.STATUS_REFUND
                billing_m.save()

        return PayBillingSerializer(billing_m)

    def validate(self, attrs):
        data = dict(attrs)
        sid = data.get('sid')
        price = data.get('price')
        # 验证签名
        self.verify_signature(data)
        billing = Billing.objects.filter(sid=sid)
        if not billing.exists():
            raise serializers.ValidationError({'sid': '订单不存在'})
        billing_m = billing.first()
        price = Decimal(price)
        if billing_m.status == billing_m.STATUS_UNPAID:
            raise serializers.ValidationError({'sid': '该订单尚未被支付'})

        if billing_m.status == billing_m.STATUS_CANCELED:
            raise serializers.ValidationError({'sid': '该订单已被取消'})

        if billing_m.status == billing_m.STATUS_DELETE:
            raise serializers.ValidationError({'sid': '该订单已被删除'})

        if price < 0:
            raise serializers.ValidationError({'price': '不能小于0'})
        if price > billing_m.price:
            raise serializers.ValidationError({'price': '不能大于订单价格'})

        return attrs


class CreateOrderSerializer(BaseSz):
    name = serializers.CharField(max_length=128, label="商品名称", help_text="商品名称")
    price = serializers.DecimalField(decimal_places=2, max_digits=12, label="价格", help_text='价格')
    gateway = serializers.CharField(default='null', allow_null=True, label="支付网关名称", max_length=64, help_text="网关")
    device_type = serializers.IntegerField(default=0, required=False, label="设备类型", help_text="0:电脑，1:手机,2:平板，默认：0")

    def _get_http_host(self):
        request = self.context.get('request', None)
        if request:
            return request.META['HTTP_HOST']

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        print(validated_data)
        name = validated_data.get('name')
        price = validated_data.get('price')
        app_id = validated_data.get('app_id')
        gateway = validated_data.get('gateway')
        device_type = validated_data.get('device_type')
        app_m = PayApplication.objects.get(app_id=app_id)
        gateway_m = PayGateway.objects.get(name=gateway)
        billing_m = Billing()
        billing_m.app = app_m
        billing_m.name = name
        billing_m.price = price
        billing_m.gateway = gateway_m
        billing_m.save()

        if settings.WEBSITE_ADDRESS == '':
            url = f'http://{self._get_http_host()}'
        else:
            url = settings.WEBSITE_ADDRESS

        pay = gateway_m.get_pay_instance()

        data = BaseTransactionSlip(sid=billing_m.sid,
                                   name=billing_m.name,
                                   price=billing_m.price,
                                   sync_url=f'{url}{gateway_m.sync_url}',
                                   async_url=f'{url}{gateway_m.async_url}',
                                   device_type=device_type)
        print(f'create order: {data}')
        create_order_res = pay.create_order(data)
        billing_m.pay_url = create_order_res.url
        billing_m.save()
        data = {'url': f'{billing_m.pay_url}', 'sid': billing_m.sid}
        return data

    def validate(self, attrs):
        data = dict(attrs)
        # 验证签名
        self.verify_signature(data)
        # 验证支付网关
        gateway = data.get('gateway', 'null')
        if gateway == 'null':
            objs = PayGateway.objects.filter(enable=True)
            if not objs.exists():
                raise serializers.ValidationError({"gateway": ["系统尚未配置一个有效的网关"]})
        else:
            objs = PayGateway.objects.filter(name=gateway, enable=True)
            if not objs.exists():
                raise serializers.ValidationError({"gateway": ["支付网关未找到或者未生效"]})
        gateway: PayGateway = objs.first()
        attrs['gateway'] = gateway.name
        return attrs
