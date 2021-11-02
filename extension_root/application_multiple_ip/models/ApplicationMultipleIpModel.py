from common.model import BaseModel
from django.db import models
from app.models import App
from django.utils.translation import ugettext_lazy as _


class ApplicationMultipleIp(BaseModel):
    """
    应用多网段IP地址对应表
    """

    app = models.ForeignKey(
        App,
        on_delete=models.PROTECT,
        verbose_name=_("应用"),
        related_name="multiple_ips"
    )

    ip_regx = models.CharField(
        verbose_name=_("网段正则表达式"),
        max_length=200
    )

    ip = models.IPAddressField(
        verbose_name=_("IP地址")
    )

    class Meta:
        verbose_name_plural = _("应用多网段IP地址对应表")
