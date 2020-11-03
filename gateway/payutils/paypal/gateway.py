import json

from django.http import HttpResponse
# Construct a request object and set desired parameters
# Here, OrdersCreateRequest() creates a POST request to /v2/checkout/orders
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersGetRequest, OrdersCaptureRequest

from gateway.payutils.abstract import AbstractPayFactory, BaseTransactionSlip, BaseTransactionResult, \
    BaseCreateOrderResult, BaseRequestRefund, BaseCancelOrder


class PayPal(AbstractPayFactory):
    config = {
        "__sandbox": False,
        "__client_id": "应用ID",
        "__client_secret": "商户私钥",
        "__currency_code": "USD",
        "__webhook_id": "xxxx",
        "#说明": "去掉 __ 启用对应的选项，#号为备注字典"
    }
    paypal = None

    def __init__(self, data: dict):
        super(PayPal, self).__init__(data)
        _env_config = {'client_id': self.config['client_id'],
                       'client_secret': self.config['client_secret']}

        if self.config['sandbox']:
            environment = SandboxEnvironment(**_env_config)
        else:
            environment = LiveEnvironment(**_env_config)
        self.paypal = PayPalHttpClient(environment)

    def create_order(self, data: BaseTransactionSlip, *args, **kwargs) -> BaseCreateOrderResult:
        if not isinstance(data, BaseTransactionSlip):
            raise RuntimeError("请传入一个 BaseTransactionSlip 实例")

        # params = {"out_trade_no": data.sid, "subject": data.name,
        #           "total_amount": data.price, "return_url": data.sync_url}
        request = OrdersCreateRequest()

        request.prefer('return=representation')

        request.request_body(
            {
                "application_context": {
                    "return_url": data.sync_url,
                    "notify_url": data.async_url

                },
                "intent": "CAPTURE",
                ''
                "purchase_units": [
                    {
                        "invoice_id": data.sid,
                        "description": data.name,
                        "amount": {
                            "currency_code": self.config['currency_code'],
                            "value": data.price
                        }
                    }
                ]
            }
        )
        response = self.paypal.execute(request)
        for link in response.result.links:
            if link.rel == 'approve':
                return BaseCreateOrderResult(link.href)

    def notify_order(self, request, *args, **kwargs) -> BaseTransactionResult:
        data = request.data

        print('收到来自 PayPal 的异步通知数据')
        print(json.dumps(data))
        # todo 需要对 PayPal 的回调进行验签
        result = BaseTransactionResult(0, 0, 0)
        return result

    def return_order(self, data: dict, *args, **kwargs) -> BaseTransactionResult:
        data = self.__deal_dict(data)
        request = OrdersGetRequest(data['token'])
        response = self.paypal.execute(request)
        order = response.result.id
        purchase_units = response.result.purchase_units[0]
        status = response.result.status
        res_status = BaseTransactionResult.UNKNOWN_PAYMENT_STATUS
        if status == 'APPROVED':
            orders_capture_request = OrdersCaptureRequest(data['token'])
            self.paypal.execute(orders_capture_request)
            res_status = BaseTransactionResult.SUCCESSFULLY_VERIFIED
        result = BaseTransactionResult(purchase_units['invoice_id'], order, res_status)
        return result

    def query_order(self, sid) -> dict:
        pass

    def cancel_order(self, sid) -> BaseCancelOrder:
        pass

    def request_refund(self, data: BaseRequestRefund) -> bool:
        pass

    @staticmethod
    def __deal_dict(data: dict):
        _data = {}
        for i in data:
            if isinstance(data[i], list):
                _data[i] = data[i][0]
            else:
                _data[i] = data[i]
        return _data

    @staticmethod
    def gateway_config() -> dict:
        return PayPal.config

    @staticmethod
    def success_http() -> HttpResponse:
        return HttpResponse('success')

    @staticmethod
    def failed_http() -> HttpResponse:
        return HttpResponse('验签出错')

    @staticmethod
    def gateway_name():
        return "PayPal"

    @staticmethod
    def gateway_description():
        return "PayPal 接口"
