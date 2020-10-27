**设计说明**

为了统一各类支付平台的支付细节而实现的一套支付系统

* 应用模块

 区分不同的业务收款
 
* 支付接口

创建订单、退款、查询支付等功能，并对整个流程实现双向验签，防止篡改

**部署**

```shell script
# 安装依赖
pip install -r requirements.txt
# 迁移数据库
python manage.py makemigrations
python manage.py migrate
#创建超级用户
python manage.py createsuperuser
```

**支付插件**

为了实现支付插件，请查阅下列代码

`gateway/payutils/abstract.py`

**待续**