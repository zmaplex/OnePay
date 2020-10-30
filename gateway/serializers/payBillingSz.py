from rest_framework import serializers, status

from gateway.models import Billing
from gateway.serializers.baseSz import BaseSz


class PayBillingSerializer(serializers.ModelSerializer):
    app = serializers.SerializerMethodField('_app', label="app id")
    gateway = serializers.SerializerMethodField('_gateway', label='网关名称')
    status_text = serializers.SerializerMethodField('_status_text', label='支付状态说明')

    class Meta:
        model = Billing
        fields = ['app', 'sid', 'pid', 'name', 'price',
                  'pay_url', 'status', 'gateway', 'status_text']

    def _app(self, obj: Billing):
        return obj.app.app_id

    def _gateway(self, obj: Billing):
        return obj.gateway.name

    def _status_text(self, obj: Billing):
        return obj.get_status_display()


class BasePayQueryBillingSerializer(BaseSz):
    """
    基础查询
    """

    sid = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    pid = serializers.CharField(max_length=64, required=False, allow_null=True, allow_blank=True)
    app_id = serializers.CharField(max_length=15, label="应用ID", help_text="应用必须是已经注册且有效")

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        sid = validated_data.get('sid', None)
        pid = validated_data.get('pid', None)
        app_id = validated_data.get('app_id', None)
        if sid:
            billing_m = Billing.objects.get(app__app_id=app_id, sid=sid)
        else:
            billing_m = Billing.objects.get(app__app_id=app_id, pid=pid)
        return PayBillingSerializer(billing_m)

    def validate(self, attrs):
        data = dict(attrs)
        sid = data.get('sid', None)
        pid = data.get('pid', None)
        app_id = data.get('app_id')

        # 验证签名
        self.verify_signature(app_id, data)

        try:
            if sid:
                Billing.objects.get(app__app_id=app_id, sid=sid)
            elif pid:
                Billing.objects.get(app__app_id=app_id, pid=pid)
            else:
                error = {
                    "sid": ["必填其中一项"],
                    "pid": ["必填其中一项"],
                }
                raise serializers.ValidationError(error)
        except Billing.DoesNotExist:
            _key = 'sid'
            if pid:
                _key = 'pid'
            error = {_key: '未查到相关记录'}
            raise serializers.ValidationError(error, code=status.HTTP_404_NOT_FOUND)
        return data
