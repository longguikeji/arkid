from django.db import models
from django.apps import AppConfig
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = 'com_longgui_auth_factor_otp'


class OTPAppConfig(AppConfig):

    name = app_label


class OTPUser(UserExpandAbstract):
    class Meta:
        app_label = app_label

    otp_secret = models.CharField(
        max_length=255, blank=True, default='', verbose_name='密钥'
    )
    otp_uri = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name='二维码URI',
    )

    is_apply = models.BooleanField(default=False, verbose_name='是否启用')
