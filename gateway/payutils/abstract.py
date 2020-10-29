import abc

from django.http import HttpResponse
from rest_framework.exceptions import ValidationError


class BaseTransactionSlip(object):
    def __init__(self, sid, name, price, sync_url, async_url=None):
        self.sid = sid
        self.name = name
        self.price = str(price)
        self.sync_url = sync_url
        self.async_url = async_url


class BaseTransactionResult(object):
    SUCCESSFULLY_VERIFIED = 0
    SIGN_VERIFICATION_FAILED = 1
    INTERNAL_EXCEPTION = 2
    UNKNOWN_PAYMENT_STATUS = 3

    def __init__(self, sid, pid, status):
        self.sid = sid
        self.pid = pid
        self.status = status

    def __str__(self):
        return f"{{'sid':{self.sid},'pid':{self.pid},'status':{self.status}}}"


class AbstractPayFactory(object):
    config = {}

    """
    子类需要声明 config 类变量，__代表字段未启用，#号为备注字段 示例如下
    config={
        "__auth_id": "授权ID",

        "__sign_id": "签名ID，注意保密",

        ...

        "#说明": "去掉 __ 启用对应的选项，并确保对应的 value 正确，#号为备注字典",
    }
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, data: dict):
        if data is None:
            raise RuntimeError("字典数据为空")
        self.set_up(data)

    def set_up(self, data: dict):
        """
        配置支付参数
        在 config={} 中填写配置项以及说明，如密钥、私钥等配置项。
        :param data:
        :return: None
        """
        if not self.config:
            raise NotImplementedError("该模块没有配置 config 类成员变量")
        items = self.config.keys()
        for item in items:
            item = item.replace("__", '')
            if item not in data and "#" not in item:
                raise ValidationError({"detail": f"请检查 {item} 选项是否存在，或者没有启用"})

        self.config = data

    @abc.abstractmethod
    def create_order(self, data: BaseTransactionSlip, *args, **kwargs):
        """
        创建订单接口
        :param data: 订单数据封装到字典中
        :param args:
        :param kwargs:
        :return: 支付URL
        """
        raise NotImplementedError("创建订单接口没有实现")

    @abc.abstractmethod
    def notify_order(self, request, *args, **kwargs) -> BaseTransactionResult:
        """
        异步通知，支付平台主动调用，处理完业务逻辑后，需要给支付平台返回一个HTTP响应\n\n
        调用 success_http 方法获取成功的响应，告诉支付平台该订单支付处理成功。\n
        调用 failed_http  方法获取失败的响应，告诉支付平台订单支支付失败。\n
        :param request: 来自支付平台的异步通知请求 <br>
        一般的 POST 数据使用 request.data.dict() 即可获取 <br>
        无法通过 django 自动格式化的数据(如微信)，请自行通过 request.body 获取原始数据进行处理。<br>
        :param args:
        :param kwargs:
        :return: BaseTransactionResult
        """
        raise NotImplementedError("异步通知接口没有实现")

    @abc.abstractmethod
    def return_order(self, data: dict, *args, **kwargs) -> BaseTransactionResult:
        """
        同步通知，验签需要支付模块自己实现，需要根据返回结果处理业务数据然后再同步跳转
        :param data: request.query_params，一般为支付平台同步调用的 GET 参数
        :param args:
        :param kwargs:
        :return:BaseTransactionResult
        """
        raise NotImplementedError("同步通知接口没有实现")

    @staticmethod
    @abc.abstractmethod
    def gateway_name() -> str:
        """
        :return: 网关名字，必须要是英文字符串且不与其他支付模块冲突
        """
        raise NotImplementedError("获取网关名字接口没有实现")

    @staticmethod
    @abc.abstractmethod
    def gateway_description() -> str:
        """
        :return:网关描述
        """
        raise NotImplementedError("获取网关描述接口没有实现")

    @staticmethod
    @abc.abstractmethod
    def gateway_config() -> dict:
        """
        必须是JSON格式的文本
        {
        ”key“:"填写密钥"，
        ”appid":"填写应用ID"
        }
        :return: 网关配置
        """
        raise NotImplementedError("获取网关配置接口没有实现")

    @staticmethod
    def get_result(pay_url, no_id):
        """
        返回支付地址
        :param pay_url:支付地址
        :param no_id: 账单id
        :return:{'id': no_id, 'url': pay_url}
        """
        return {'id': no_id, 'url': pay_url}

    @staticmethod
    @abc.abstractmethod
    def success_http() -> HttpResponse:
        """
        实现支付成功的HTTP返回请求
        :return: HttpResponse
        """
        raise NotImplementedError("支付成功的HTTP返回请求接口没有实现")

    @staticmethod
    @abc.abstractmethod
    def failed_http() -> HttpResponse:
        """
        实现支付失败的HTTP返回请求
        :return: HttpResponse
        """
        raise NotImplementedError("支付失败的HTTP返回请求接口没有实现")