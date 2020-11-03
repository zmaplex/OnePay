from gateway.payutils.alipay.gateway import AliaPay
from gateway.payutils.paypal.gateway import PayPal

# 这里注册支付模块
PAY_MODULES = [PayPal, AliaPay]
