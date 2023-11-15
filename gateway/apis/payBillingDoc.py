from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter
from gateway.serializers.payBillingSz import PayBillingSerializer

base_pay_billing_view__query_order = {
    "summary": "查询一个订单详情",
    "description": "查询本系统的订单数据",
    "parameters": [
        OpenApiParameter(
            name="sid",
            required=False,
            location=OpenApiParameter.QUERY,
            description="本系统账单id",
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="pid",
            required=False,
            location=OpenApiParameter.QUERY,
            description="支付平台账单id",
            type=OpenApiTypes.STR,
        ),
        OpenApiParameter(
            name="app_id",
            location=OpenApiParameter.QUERY,
            description="应用id",
            type=OpenApiTypes.INT,
        ),
        OpenApiParameter(
            name="sign",
            location=OpenApiParameter.QUERY,
            description="签名",
            type=OpenApiTypes.STR,
        ),
    ],
    "responses": {200: PayBillingSerializer},
}
