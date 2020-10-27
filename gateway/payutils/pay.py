import traceback

from gateway.models import PayGateway
from gateway.payutils.abstract import AbstractPayFactory
from .config import PAY_MODULES


class Pay(object):
    PAY_MODULES_INFO = []

    @staticmethod
    def init():
        """
        第一次使用必须要初始化
        :return:
        """
        for module_item in PAY_MODULES:
            try:
                Pay.__register_module(module_item)
            except Exception as e:
                print(f"添加支付模块出错，{traceback.format_exc()}")
        Pay.__load_module()

    @staticmethod
    def re_init():
        """
        重新初始化
        :return:
        """
        Pay.PAY_MODULES_INFO = []
        Pay.init()

    @staticmethod
    def get_instance(name, config: dict = None) -> AbstractPayFactory:
        """
        获取支付模块的实例
        :param name: 支付模块的名称
        :param config:支付模块的配置信息
        :return: AbstractPayFactory
        """
        for item in Pay.PAY_MODULES_INFO:
            if item["name"] != name:
                continue
            obj_class = PAY_MODULES[item["id"]]
            # 初始化具体的支付类
            return obj_class(config)
        raise RuntimeError(f"没有找到{name}支付模块")

    @staticmethod
    def __load_module():
        """
        运行时载入已注册的支付模块到内存中，在业务系统中调用支付模块时会校验相关配置数据，不通过会抛出运行时异常。
        如果您有一定开发能力遇到异常请不要捕获，根据异常信息即时修改支付配置数据即可，对于无开发能力的用户，建议付费寻求技术支援。
        :return:
        """
        for index, _module in enumerate(PAY_MODULES):
            m_info = {"id": index, "name": _module.gateway_name(), "description": f"{_module.gateway_description()}"}
            Pay.PAY_MODULES_INFO.append(m_info)
            print(f"载入接口：{m_info}")

    @staticmethod
    def __register_module(module_item):
        """
        注册支付模块信息到数据库中，初次注册的时候，请到系统修改配置信息并启用
        :return:
        """
        obj, created = PayGateway.objects.get_or_create(name=module_item.gateway_name())

        if created:
            print(f"添加接口 {module_item.gateway_name()}")
            obj.description = module_item.gateway_description()
            obj.save()
            obj.pay_config = module_item.gateway_config()
            obj.async_url = f"/api/PayGateway/PayGateway/{obj.name}/async_notify/"
            obj.sync_url = f"/api/PayGateway/PayGateway/{obj.name}/sync_notify/"
            obj.save()
