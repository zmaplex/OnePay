from django.conf import settings
from rest_framework import serializers

from gateway.models import PayGateway, PayApplication, Billing
from gateway.payutils.abstract import BaseTransactionSlip
from gateway.payutils.pay import Pay
from gateway.serializers.baseSz import BaseSz


class PayGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayGateway
        fields = ['id', 'name', 'alias_name', 'enable', 'description']


class CreateOrderSerializer(BaseSz):
    name = serializers.CharField(max_length=128, label="商品名称", help_text="商品名称")
    price = serializers.DecimalField(decimal_places=2, max_digits=12, label="价格", help_text='价格')
    gateway = serializers.CharField(default='null', allow_null=True, label="支付网关名称", max_length=64, help_text="网关")
    app_id = serializers.CharField(max_length=15, label="应用ID", help_text="应用必须是已经注册且有效")

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
        config = gateway_m.pay_config
        pay = Pay.get_instance(gateway_m.name, config)
        data = BaseTransactionSlip(sid=billing_m.sid,
                                   name=billing_m.name,
                                   price=billing_m.price,
                                   sync_url=f'{url}{gateway_m.sync_url}',
                                   async_url=f'{url}{gateway_m.async_url}')
        print(f'create order: {data}')
        pay_url = pay.create_order(data)
        billing_m.pay_url = pay_url
        billing_m.save()
        data = {'url': f'{pay_url}', 'sid': billing_m.sid}
        return data

    def validate(self, attrs):
        data = dict(attrs)
        app_id = data.get('app_id')
        # 验证签名
        self.verify_signature(app_id, data, ['sign'])
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
