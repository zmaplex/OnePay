from gateway.payutils.alipay.gateway import AliaPay
from gateway.payutils.pmpay.gateway import PMAliaPay

# 这里注册支付模块
PAY_MODULES = [PMAliaPay, AliaPay]
