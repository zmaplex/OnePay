from drf_yasg import openapi

from gateway.serializers.payBillingSz import PayBillingSerializer

base_pay_billing_view__query_order = {
    'operation_summary': '查询本系统的订单数据',
    'manual_parameters': [
        openapi.Parameter(name='sid', required=False, in_=openapi.IN_QUERY, description='本系统账单id',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='pid', required=False, in_=openapi.IN_QUERY, description='支付平台账单id',
                          type=openapi.TYPE_STRING),
        openapi.Parameter(name='app_id', in_=openapi.IN_QUERY, description='应用id', type=openapi.TYPE_STRING),
        openapi.Parameter(name='sign', in_=openapi.IN_QUERY, description='签名', type=openapi.TYPE_STRING),
    ],
    'responses': {200: openapi.Response('response description', PayBillingSerializer)}
}
