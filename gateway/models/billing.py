from datetime import datetime

from django.db import models

# Create your models here.
from common.model.CommonModel import CommonModel
from gateway.models.application import PayApplication
from gateway.models.gateway import PayGateway


def get_nid():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


class Billing(CommonModel):
    """
    账单
    """
    STATUS_UNPAID = 0
    STATUS_PAID = 1
    STATUS_DELETE = 2
    STATUS_CANCELED = 3
    STATUS_REFUND = 4

    STATUS_CHOICES = [
        (STATUS_UNPAID, '未支付'), (STATUS_PAID, '已支付'), (STATUS_DELETE, '已删除'),
        (STATUS_CANCELED, '被取消'), (STATUS_REFUND, '已退款'),
    ]
    app = models.ForeignKey(
        PayApplication, on_delete=models.SET_NULL, null=True)
    sid = models.CharField(max_length=20, unique=True,
                           default=get_nid, verbose_name="唯一编号",
                           help_text="系统账单唯一ID")
    pid = models.CharField(max_length=64, verbose_name="交易号", null=True,
                           help_text="支付平台创建的交易号")
    name = models.CharField(max_length=128, verbose_name="名称")
    price = models.DecimalField(
        max_digits=18, decimal_places=2, verbose_name="价格")
    pay_url = models.CharField(max_length=1024, verbose_name="支付地址", null=True)
    status = models.IntegerField(
        default=STATUS_UNPAID, choices=STATUS_CHOICES, verbose_name="状态")
    gateway = models.ForeignKey(PayGateway, on_delete=models.CASCADE,
                                verbose_name="网关")

    class Meta:
        verbose_name = "交易记录"
        verbose_name_plural = "交易记录"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
