**设计说明**

> 预发布阶段，请勿部署生产环境

为了统一各类支付平台的支付细节而实现的一套支付系统

- 接口文档

运行服务后，访问 http://127.0.0.1:8000/docs/schema/swagger-ui/#/

**功能说明**

> 系统流程

[支付平台]  <--支付插件-->  [聚合系统]  <--统一接口-->  [应用]

> 三大基本功能

- 创建订单
- 原路退款
- 查询订单

> 安全说明

- [支付平台]  <--支付插件--> [聚合系统]

  - 按照平台标准实现相关接口
  
- [聚合系统]  <--统一接口--> [应用]

  - 双向流程使用 2048 位的 RSA私钥加密以及对应公钥进行验签(RSAwithSHA256)

**部署**

```shell script
# 使用虚拟环境
python3 -m venv dj_venv
# 激活虚拟环境
source dj_venv/bin/activate
# 安装依赖
pip install -r requirements.txt
# 复制并修改配置文件
cp .env.template .env && vim .env
# 迁移数据库
python manage.py makemigrations
python manage.py migrate
# 创建超级用户
python manage.py createsuperuser
# 复制静态资源
python manage.py collectstatic
# 启用
source dj_venv/bin/activate && dj_venv/bin/gunicorn --worker-class=gevent --worker-connections=1000 --workers=3  --bind unix:/var/run/jcpmpay.sock JCPMPay.wsgi:application
```

**支付插件**

注意：目前插件规范处于预发布阶段，生产环境请勿使用。

- 支付插件的抽象类

  - [Abstract](https://github.com/zmaplex/JCPMPay/blob/master/gateway/payutils/abstract.py)

- 支付宝 接口实现

  - [Alipay](https://github.com/zmaplex/JCPMPay/blob/master/gateway/payutils/alipay/gateway.py)

- PayPal 接口实现

  - [PayPal](https://github.com/zmaplex/JCPMPay/blob/master/gateway/payutils/paypal/gateway.py)


**nginx 配置参考**
```
    ...
    location / {
      proxy_pass http://unix:/var/run/jcpmpay.sock;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /static {
      autoindex on;
      alias  /your_project_directory/static;
    }
    
    location /media {
      autoindex on;
      alias  /your_project_directory/media;
    }
    ...
```
**待续**
