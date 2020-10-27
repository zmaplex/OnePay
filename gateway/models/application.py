import base64
import time
import urllib.parse

from Crypto.PublicKey import RSA
from django.db import models

# Create your models here.
from common.model.CommonModel import CommonModel
from gateway.utils import RSASignatureTool


def get_app_id():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())


def get_platform_private_key():
    x = RSA.generate(2048)
    s_key = x.export_key()
    return s_key.decode("utf-8")


class PayApplication(CommonModel):
    REVIEW = 0
    ONLINE = 1
    SUSPENDED = 2
    OFFLINE = 3
    DELETED = 4

    CHOICES = [
        (REVIEW, '审查中'), (ONLINE, '已上线'), (SUSPENDED, '被暂停'),
        (OFFLINE, '已下线'), (DELETED, '被删除'),
    ]
    own = models.IntegerField(default=1, help_text="保留字段")
    name = models.CharField(max_length=64, help_text="应用名字")
    app_id = models.CharField(default=get_app_id, max_length=15, unique=True,
                              verbose_name="应用ID", help_text="系统分配的应用ID")

    notify_url = models.CharField(
        max_length=256, verbose_name="异步通知", help_text="网站异步回调地址")
    sync_url = models.CharField(
        max_length=256, verbose_name="同步通知", help_text="网站同步回调地址")
    status = models.IntegerField(
        default=REVIEW, choices=CHOICES, verbose_name="状态", help_text="状态")
    merchant_public_key = models.TextField(
        max_length=2048, verbose_name="商户公钥", help_text="开发者上传的公钥 pkcs8 格式")
    platform_private_key = models.TextField(
        max_length=2048, verbose_name="平台私钥", default=get_platform_private_key,
        help_text="商户私钥 pkcs8 格式")

    def is_valid(self):
        return self.status == self.ONLINE

    def get_sync_notify_to_merchant_url(self, data: dict):
        """
        生成商户的同步地址
        @param data: 返回参数，必须含有签名字段
        @return:
        """
        if not self.sync_url:
            return
        params = urllib.parse.urlencode(data)
        return f'{self.sync_url}?{params}'

    def to_verify_with_public_key(self, signature, plain_text):
        # 商户传来的数据，使用商户公钥进行验签
        public = self.merchant_public_key
        signature = base64.b64decode(signature.encode())
        return RSASignatureTool.to_verify_with_public_key(public, signature, plain_text)

    def to_sign_with_platform_private_key(self, data: dict) -> str:
        """
        使用平台密钥进行签名
        @param data:
        @return:
        """
        signature_string = RSASignatureTool.sort_argv(data)
        signature = RSASignatureTool.to_sign_with_private_key(self.platform_private_key, signature_string)
        signature = RSASignatureTool.to_base64(signature)
        return signature

    def get_platform_public_key(self):
        """
        获取平台公钥
        @return:
        """
        s_key = self.platform_private_key
        p_key = RSASignatureTool.get_public_key_from_private_key(s_key)
        return p_key

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "接入应用"
        verbose_name_plural = "接入应用"
