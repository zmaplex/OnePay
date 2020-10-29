from django.db import models

# Create your models here.
from common.model.CommonModel import CommonModel


class PayGateway(CommonModel):
    class Meta:
        verbose_name = "支付网关"
        verbose_name_plural = "支付网关"

    name = models.CharField(max_length=32, unique=True,
                            verbose_name="支付网关", help_text="必须是英文，且唯一")
    enable = models.BooleanField(default=False, verbose_name="启用")
    alias_name = models.CharField(
        max_length=30, default="", verbose_name="显示别名")
    sync_url = models.CharField(
        max_length=512, blank=True, verbose_name="同步通知地址", help_text="支付完后跳转的地址")
    async_url = models.CharField(
        max_length=512, blank=True, verbose_name="异步通知地址", help_text="支付平台主动GET的地址")
    pay_config = models.JSONField(
        max_length=20480, blank=True, null=True, default=dict, verbose_name="配置文件", help_text="支付配置方式")
    description = models.CharField(
        max_length=1024, blank=True, default="", verbose_name="支付网关描述")

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
