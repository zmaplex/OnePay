from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from drf_yasg import openapi
from rest_framework import serializers

from gateway.serializers.payBillingSz import PayBillingSerializer
from gateway.serializers.payGatewaySz import PayGatewaySerializer

base_pay_gateway_view__request_refund = {
    'summary': '退款接口',
    'description': '根据 status 判断账单状态',
    'responses': {200: PayBillingSerializer}
}

base_pay_gateway_view__cancel_order_Response = {
    "detail": {
        "status": "操作状态，False 或者 True",
        "platform_detail": "支付平台返回的信息，json 格式"
    }
}


class OpenApiCancelOrderDetailSerializer(serializers.Serializer):
    detail = serializers.BooleanField(default=False, label="操作状态", help_text="True:取消订单成功")
    platform_detail = serializers.JSONField(label="支付平台附加信息", help_text="支付平台附加信息")


class OpenApiCancelOrderResSerializer(serializers.Serializer):
    detail = OpenApiCancelOrderDetailSerializer()


class OpenApiCreateOrderResSerializer(serializers.Serializer):
    url = serializers.CharField(label="支付地址")
    sid = serializers.CharField(label="系统订单")


class OpenApiNotifyResSerializer(serializers.Serializer):
    sid = serializers.CharField(label="订单ID", help_text="本系统订单ID")
    pid = serializers.CharField(label="平台订单ID", help_text="支付平台生成的账单ID")
    msg = serializers.CharField(label="消息", help_text="默认：null,保留字段")
    name = serializers.CharField(label="账单名称", help_text="商户创建订单的名称")
    price = serializers.CharField(label="价格", help_text="实际成交的价格")
    pay_status = serializers.CharField(label="支付状态", help_text="支付状态。<br>unknown：支付状态未知<br>successful:成功支付")
    last_modify = serializers.CharField(label="最后修改时间", help_text="订单更新时间")


base_pay_gateway_view__list = {
    'summary': '获取所有启用网关',
    'description': '获取所有启用的网关，后续接口所需网关参数都是网关的 name 字段内容（英文）',
    'responses': {200: PayGatewaySerializer}
}

base_pay_gateway_view__create_order = {
    'summary': '创建订单接口数据',
    'description': '创建订单数据，gateway 默认为 null 时，系统将使用第一个有效的网关插件',
    'responses': {200: OpenApiCreateOrderResSerializer}
}

base_pay_gateway_view__sync_notify = {
    'summary': '同步通知接口',
    'tags': ['Gateway', 'BaseGateway'],
    'description': '完成支付后，本系统会携带GET参数重定向到应用设置的同步地址.',
    'responses': {301: OpenApiNotifyResSerializer}
}

base_pay_gateway_view__async_notify = {
    'summary': '异步通知接口',
    'tags': ['Gateway', 'BaseGateway'],
    'description': '当用户支付成功后，本系统会POST数据到应用设置的异步地址中。<br>'
                   '当应用响应失败时，系统会通知支付平台处理失败，直至应用响应成功为止。<br>'
                   '失败重试的次数以支付平台具体规则为准，系统收到支付平台每一次回调通知，都会通知应用一次。',
    'responses': {200: OpenApiNotifyResSerializer}
}


class OpenApiQueryOrderResSerializer(serializers.Serializer):
    detail = serializers.JSONField(help_text="支付平台订单的原始信息，json 结构。不保证统一的数据结构，请自行处理其中的差异。")


base_pay_gateway_view__query_order = {
    'summary': '查询平台订单信息',
    'description': '直接向支付平台查询订单信息',
    'parameters': [
        OpenApiParameter(name='sid', required=False, location=OpenApiParameter.QUERY, description='本系统账单id',
                         type=OpenApiTypes.STR),
        OpenApiParameter(name='app_id', location=OpenApiParameter.QUERY, description='应用id', type=OpenApiTypes.STR),
        OpenApiParameter(name='sign', location=OpenApiParameter.QUERY, description='签名', type=OpenApiTypes.STR),
    ],
    'responses': {200: OpenApiQueryOrderResSerializer}
}

base_pay_gateway_view__cancel_order = {
    'summary': '关闭尚未支付的订单',
    'description': '关闭尚未支付的订单,有些支付平台可能不支持这个特性，系统会返回错误信息',
    'parameters': [
        OpenApiParameter(name='sid', required=False, location=OpenApiParameter.QUERY,
                         description='本系统账单id', type=OpenApiTypes.STR),
        OpenApiParameter(name='app_id', location=OpenApiParameter.QUERY,
                         description='应用id', type=OpenApiTypes.STR),
        OpenApiParameter(name='sign', location=OpenApiParameter.QUERY,
                         description='签名', type=OpenApiTypes.STR),
    ],
    'responses': {
        200: OpenApiCancelOrderResSerializer}
}
