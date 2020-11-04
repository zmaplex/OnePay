from alipay import AliPay
from django.http import HttpResponse

from gateway.payutils.abstract import AbstractPayFactory, BaseTransactionSlip, BaseTransactionResult, \
    BaseCreateOrderResult, BaseRequestRefund, BaseCancelOrder, BaseOrderId


class AliaPay(AbstractPayFactory):
    config = {
        "__sandbox": False,
        "__app_id": "支付宝开发者应用ID",
        "__private_key": "商户私钥",
        "__public_key": "支付宝公钥",
        "#说明": "去掉 __ 启用对应的选项，#号为备注字典"
    }
    alipay = None

    def __init__(self, data: dict):
        super(AliaPay, self).__init__(data)
        if self.config['sandbox']:
            self.url = "https://openapi.alipaydev.com/gateway.do?"
        else:
            self.url = "https://openapi.alipay.com/gateway.do?"
        self.alipay = AliPay(
            appid=self.config["app_id"],
            app_notify_url=None,  # 默认回调url
            app_private_key_string=self.config["private_key"],
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=self.config["public_key"],
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False,  # 默认False
        )

    def create_order(self, data: BaseTransactionSlip, *args, **kwargs) -> BaseCreateOrderResult:
        if not isinstance(data, BaseTransactionSlip):
            raise RuntimeError("请传入一个 BaseTransactionSlip 实例")

        params = {"out_trade_no": data.sid, "subject": data.name,
                  "total_amount": data.price, "return_url": data.sync_url}
        if data.async_url:
            params['notify_url'] = data.async_url

        if data.device_type == data.COMPUTER_DEVICE:
            order_string = self.alipay.api_alipay_trade_page_pay(**params)
        else:
            order_string = self.alipay.api_alipay_trade_wap_pay(**params)

        return BaseCreateOrderResult(self.url + order_string)

    def notify_order(self, request, *args, **kwargs) -> BaseTransactionResult:
        data = request.data
        if not isinstance(data, dict):
            data = dict(request.data.dict())
        data = self.__deal_dict(data)

        signature = data.pop("sign")
        success = self.alipay.verify(data, signature)
        sid = data["out_trade_no"]
        pid = data["trade_no"]
        status = BaseTransactionResult.SIGN_VERIFICATION_FAILED
        if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            status = BaseTransactionResult.SUCCESSFULLY_VERIFIED
        result = BaseTransactionResult(sid, pid, status)
        return result

    def return_order(self, data: dict, *args, **kwargs) -> BaseTransactionResult:
        data = self.__deal_dict(data)
        # verification
        signature = data.pop("sign")
        success = self.alipay.verify(data, signature)
        sid = data["out_trade_no"]
        pid = data["trade_no"]
        status = BaseTransactionResult.SIGN_VERIFICATION_FAILED
        if success:
            status = BaseTransactionResult.UNKNOWN_PAYMENT_STATUS
        result = BaseTransactionResult(sid, pid, status)
        return result

    def query_order(self, data: BaseOrderId) -> dict:
        res = self.alipay.api_alipay_trade_query(out_trade_no=data.sid)
        return res

    def cancel_order(self, data: BaseOrderId) -> BaseCancelOrder:
        res = self.alipay.api_alipay_trade_close(out_trade_no=data.sid)
        res_status = False
        if '10000' in res and 'Success' in res:
            res_status = True
        return BaseCancelOrder(res_status, res)

    def request_refund(self, data: BaseRequestRefund) -> bool:
        result = self.alipay.api_alipay_trade_refund(out_trade_no=data.sid,
                                                     refund_amount=f"{data.price}")
        if result["code"] == "10000":
            return True
        else:
            return False

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
        return AliaPay.config

    @staticmethod
    def success_http() -> HttpResponse:
        return HttpResponse('success')

    @staticmethod
    def failed_http() -> HttpResponse:
        return HttpResponse('验签出错')

    @staticmethod
    def gateway_name():
        return "AliPay"

    @staticmethod
    def gateway_description():
        return "支持手机、PC支付，该接口仅限于中国大陆用户"
