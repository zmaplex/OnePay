import traceback

from common.apps import BaseConfig


class GatewayConfig(BaseConfig):
    name = 'gateway'
    verbose_name = "网关"

    def ready(self):
        try:
            self.init_config()
        except Exception as e:
            self.log_msg("初始化失败")
            self.log_msg(traceback.format_exc())
        self.log_msg("初始化成功")

    def init_config(self):

        from .payutils.pay import Pay
        Pay.init()
