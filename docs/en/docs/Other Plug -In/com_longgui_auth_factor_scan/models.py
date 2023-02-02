from django.db import models
from django.apps import AppConfig
from arkid.core.translation import gettext_default as _
from arkid.core.models import User
from arkid.common.model import BaseModel

app_label = "com_longgui_auth_factor_scan"


class ScanAppConfig(AppConfig):

    name = app_label


class UserQRCode(BaseModel):

    STATUS_CHOICES = (
        ('created', _('QRCode Created', '二维码已创建')),
        ('scanned', _('QRCode Scanned', '二维码已扫描')),
        ('confirmed', _('QRCode Confirmed', '二维码已确认')),
        ('canceled', _('QRCode Canceled', '二维码已取消')),
    )

    class Meta:
        app_label = app_label

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User', '用户'),
        related_name="qrcode_set",
        related_query_name="qrcodes",
        blank=True,
        null=True,
    )
    qrcode_id = models.CharField(_("QRCode ID", "二维码ID"), max_length=256)
    session_key = models.CharField(
        _("Client Session key", "客户端Session Key"), default='', max_length=256
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="created",
        max_length=50,
        verbose_name=_('Status', "状态"),
    )
    expired_at = models.DateTimeField(blank=True, null=True, verbose_name='过期时间')
