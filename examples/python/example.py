from examples.python.utils import JCPay

domain = ""
app_id = "20201029200917"
private_key = """-----BEGIN PRIVATE KEY-----
....
-----END PRIVATE KEY-----"""
platform_public_key = """
"""
JCPay(domain, app_id, private_key, platform_public_key)
pay = JCPay(domain, app_id, private_key, platform_public_key)
pay.set_gateway('AliPay')

# 创建订单，记住 sid 号，并打开支付链接支付
pay.create("测试订单")

# 输入 sid，先本系统查询订单信息，返回结构是统一的
pay.query('20210128205836947850')

# 输入 sid，向支付网关平台查询支付订单信息，结构需要自行处理。
pay.query_gateway_platform('20210128205836947850')
