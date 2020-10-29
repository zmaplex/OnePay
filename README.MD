**设计说明**

！！！ 简陋的开发版本，接口尚未稳定，请谨慎使用

为了统一各类支付平台的支付细节而实现的一套支付系统

* 应用模块

 区分不同的业务收款
 
* 支付接口

创建订单、退款、查询支付等功能，并对整个流程实现双向验签，防止篡改

**部署**

```shell script
# 使用虚拟环境
python3 -m venv dj_venv
# 激活虚拟环境
source dj_env/bin/activate
# 安装依赖
pip install -r requirements.txt
# 复制并修改配置文件
cp .env.template .env && vim .env
# 迁移数据库
python manage.py makemigrations
python manage.py migrate
# 创建超级用户
python manage.py createsuperuser
```

**支付插件**

注意：目前接口处于不稳定状态，随时都有可能变更接口规范，请勿部署生产环境。

支付插件的实现规范，请查阅下列代码

`gateway/payutils/abstract.py`

支付宝接口简易实现，可参考

`gateway/payutils/alipay/gateway.py`

**待续**