import hashlib


class PayUtil(object):
    """
    auth_id 为 uuid ， 但是不能带 -
    sign_id 为 uuid ， 但是不能带 -
    """

    def __init__(self, auth_id, sign_id):
        self.auth_id = auth_id.replace("-", "")
        self.sign_id = sign_id.replace("-", "")

    @staticmethod
    def sign_message(**kwarg):
        """
        uuid : 支付宝账单id，\n
        no_id：客户的账单id，\n
        code：客户的业务代码，\n
        status：支付状态：success or failed，\n
        auth_id: 授权id，        （回调参数没有，需要自己保持）\n
        sign_code：uuid种子代码，（回调参数没有，需要自己保存）\n
        :param args:
        :param kwarg:
        :return:
        """
        messages = kwarg['uuid'] + \
                   kwarg['no_id'] + \
                   kwarg['code'] + \
                   kwarg['status'] + \
                   kwarg['auth_id'] + \
                   kwarg['sign_code']
        sha512 = hashlib.sha512(messages.encode("utf-8"))
        sign_str = sha512.hexdigest()
        return sign_str

    def verify_data(self, data: dict, message="模拟客户同步回调"):
        print(f"========{message}=========")
        print(f"接受到的数据{data}")
        print(self.auth_id)
        print(self.sign_id)
        sign_str = self.sign_message(uuid=data['uuid'],
                                     no_id=data['no'],
                                     code=data['code'],
                                     status=data['res'],
                                     auth_id=self.auth_id,
                                     sign_code=self.sign_id)
        print(f"本地算出的签名：{sign_str} \n服务器消息签名：{data['sign']}")
        print(f"========{message}=========")
        return sign_str == data['sign']
