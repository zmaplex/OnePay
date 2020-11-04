import json

from django.http import HttpResponse
# Construct a request object and set desired parameters
# Here, OrdersCreateRequest() creates a POST request to /v2/checkout/orders
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersGetRequest, OrdersCaptureRequest
from paypalcheckoutsdk.payments import CapturesRefundRequest
from rest_framework import status

from gateway.payutils.abstract import AbstractPayFactory, BaseTransactionSlip, BaseTransactionResult, \
    BaseCreateOrderResult, BaseRequestRefund, BaseCancelOrder, BaseOrderId
from gateway.payutils.paypal.utils import PayPalResultFormatUtil


class PayPal(AbstractPayFactory):
    config = {
        "__sandbox": False,
        "__client_id": "应用ID",
        "__client_secret": "商户私钥",
        "__currency_code": "USD",
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
                    "return_url": data.sync_url

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
        print("创建订单数据")
        self.__print_paypal_response(response)
        for link in response.result.links:
            if link.rel == 'approve':
                return BaseCreateOrderResult(link.href)

    def notify_order(self, request, *args, **kwargs) -> BaseTransactionResult:
        data = request.data
        token = data['resource']['id']
        _sid, _pid, _status = self.__order_get_request(token)
        if _status == 'APPROVED':
            orders_capture_request = OrdersCaptureRequest(data['token'])
            capture_res = self.paypal.execute(orders_capture_request)
            print(f"确认{token}订单并收款")
            self.__print_paypal_response(capture_res)
            res_status = BaseTransactionResult.SUCCESSFULLY_VERIFIED
            result = BaseTransactionResult(_sid, _pid, res_status)
        elif _status == 'COMPLETED':
            res_status = BaseTransactionResult.SUCCESSFULLY_VERIFIED
            result = BaseTransactionResult(_sid, _pid, res_status)
        else:
            res_status = BaseTransactionResult.SIGN_VERIFICATION_FAILED
            result = BaseTransactionResult(_sid, _pid, res_status)
        return result

    def return_order(self, data: dict, *args, **kwargs) -> BaseTransactionResult:
        data = self.__deal_dict(data)
        _sid, _pid, _status = self.__order_get_request(data['token'])
        res_status = BaseTransactionResult.UNKNOWN_PAYMENT_STATUS
        if _status == 'APPROVED':
            orders_capture_request = OrdersCaptureRequest(data['token'])
            capture_res = self.paypal.execute(orders_capture_request)
            print(f"确认{_pid}订单并收款")
            self.__print_paypal_response(capture_res)
            res_status = BaseTransactionResult.SUCCESSFULLY_VERIFIED
        result = BaseTransactionResult(_sid, _pid, res_status)
        return result

    def __order_get_request(self, token):
        request = OrdersGetRequest(token)
        response = self.paypal.execute(request)
        print(f"查询 {token} 订单数据")
        self.__print_paypal_response(response)
        _pid = response.result.id
        _purchase_units = response.result.purchase_units[0]
        _status = response.result.status
        _sid = _purchase_units['invoice_id']
        return _sid, _pid, _status

    def query_order(self, data: BaseOrderId) -> dict:
        request = OrdersGetRequest(data.pid)
        response = self.paypal.execute(request)
        json_data = PayPalResultFormatUtil.object_to_json(response.result)
        return json_data

    def cancel_order(self, data: BaseOrderId) -> BaseCancelOrder:
        pass

    def request_refund(self, data: BaseRequestRefund) -> bool:

        request = OrdersGetRequest(data.pid)
        response = self.paypal.execute(request)
        capture_id = response.result.purchase_units[0].payments.captures[0].id
        print(f"退款数据 {capture_id}")
        self.__print_paypal_response(response)

        request = CapturesRefundRequest(capture_id)
        request.prefer("return=representation")
        _post_data = {
            "amount": {
                "value": f"{data.price}",
                "currency_code": self.config['currency_code']
            }
        }

        request.request_body(_post_data)
        try:
            response = self.paypal.execute(request)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def __print_paypal_response(response):
        data = PayPalResultFormatUtil.object_to_json(response)
        print(json.dumps(data))

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
        """
        When your app receives the notification message, it must respond with an HTTP 200-level status code.
        If your app responds with any other status code, PayPal tries to resend the notification message
        25 times over the course of three days.
        @return: HttpResponse 200
        """
        return HttpResponse('success', status=status.HTTP_200_OK)

    @staticmethod
    def failed_http() -> HttpResponse:
        return HttpResponse('failed', status=status.HTTP_409_CONFLICT)

    @staticmethod
    def gateway_name():
        return "PayPal"

    @staticmethod
    def gateway_description():
        return "PayPal 接口"
