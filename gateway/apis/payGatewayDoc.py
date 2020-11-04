import json

from drf_yasg import openapi
from rest_framework import serializers

from gateway.serializers.payBillingSz import PayBillingSerializer

base_pay_gateway_view__request_refund = {

    'responses': {200: openapi.Response('response description', PayBillingSerializer)}
}


class OpenApiCreateOrderResSerializer(serializers.Serializer):
    url = serializers.CharField(label="支付地址")
    sid = serializers.CharField(label="系统订单")


base_pay_gateway_view__create_order = {
    'operation_summary': '创建订单接口数据',

    'responses': {200: openapi.Response('直接调用 url 即可跳转支付', OpenApiCreateOrderResSerializer)}
}

base_pay_gateway_view__query_order = {
    'operation_summary': '直接向支付平台查询订单信息',
    'manual_parameters': [
        openapi.Parameter(name='sid', required=False, in_=openapi.IN_QUERY, description='本系统账单id',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='app_id', in_=openapi.IN_QUERY, description='应用id', type=openapi.TYPE_STRING),
        openapi.Parameter(name='sign', in_=openapi.IN_QUERY, description='签名', type=openapi.TYPE_STRING),
    ],
    'responses': {200: openapi.Response('支付平台订单的原始信息，json 结构。不保证统一的数据结构，请自行处理其中的差异。')}
}

base_pay_gateway_view__cancel_order_Response = {
    "detail": {
        "status": "操作状态，False 或者 True",
        "platform_detail": "支付平台返回的信息，json 格式"
    }
}
base_pay_gateway_view__cancel_order = {
    'operation_summary': '关闭尚未支付的订单',
    'manual_parameters': [
        openapi.Parameter(name='sid', required=False, in_=openapi.IN_QUERY, description='本系统账单id',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='app_id', in_=openapi.IN_QUERY, description='应用id', type=openapi.TYPE_STRING),
        openapi.Parameter(name='sign', in_=openapi.IN_QUERY, description='签名', type=openapi.TYPE_STRING),
    ],
    'responses': {
        200: openapi.Response(json.dumps(base_pay_gateway_view__cancel_order_Response, indent=4, ensure_ascii=False))}
}