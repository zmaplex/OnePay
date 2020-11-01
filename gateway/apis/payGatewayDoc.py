from drf_yasg import openapi

from gateway.serializers.payBillingSz import PayBillingSerializer

base_pay_gateway_view__request_refund = {

    'responses': {200: openapi.Response('response description', PayBillingSerializer)}
}
