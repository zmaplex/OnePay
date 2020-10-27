import json

import requests
from django.http import HttpResponse

from gateway.payutils.abstract import AbstractPayFactory
from gateway.payutils.pmpay.utils import PayUtil


class PMAliaPay(AbstractPayFactory):
    config = {
        "__create_order_url": "创建订单的API",
        "__auth_id": "授权ID",
        "__sign_id": "签名ID，注意保密",
        "#说明": "去掉 __ 启用对应的选项，#号为备注字典"
    }

    def create_order(self, data: dict, *args, **kwargs):
        billing = data["billing"]
        if data["pay_device"] == 1:
            pay_client = "mobile"
        else:
            pay_client = "pc"
        payload = {"auth_id": self.config["auth_id"],
                   "name": billing["name"],
                   "no": billing["id"],
                   "code": billing["product_billing"],
                   "price": billing["price"],
                   "pay_type": pay_client}

        host = self.config["create_order_url"]
        response = requests.request("POST", host, data=json.dumps(payload))

        data = response.json()
        return self.get_result(no_id=data["code"], pay_url=data['url'])

    def notify_order(self, data, *args, **kwargs):
        util = PayUtil(self.config["auth_id"], self.config["sign_id"])
        res = {"status": 0, "id": data["no"]}
        if util.verify_data(data, "异步通知"):
            return res
        else:
            res["status"] = 1
            return res

    def return_order(self, data, *args, **kwargs):
        util = PayUtil(self.config["auth_id"], self.config["sign_id"])
        res = {"status": 0, "id": data["no"]}
        if util.verify_data(data, "同步通知"):
            return res
        else:
            res["status"] = 1
            return res

    @staticmethod
    def gateway_name():
        return "支付宝-朴妙接口"

    @staticmethod
    def gateway_description():
        return "朴妙软件工作室提供支持，支持手机、PC支付，该接口仅限于中国大陆用户"

    @staticmethod
    def gateway_config() -> dict:
        return PMAliaPay.config

    @staticmethod
    def success_http() -> HttpResponse:
        return HttpResponse('success')

    @staticmethod
    def failed_http() -> HttpResponse:
        return HttpResponse('验签出错')


if __name__ == '__main__':
    PMAliaPay.gateway_config()
    a = PMAliaPay({})
