from django.db import models
from django.apps import AppConfig
from arkid.core.translation import gettext_default as _
from arkid.core.models import App, User

app_label = "com_longgui_app_protocol_multiaccount"


class MultiaccountAppConfig(AppConfig):

    name = app_label


class UserApplicationAccount(models.Model):
    class Meta:
        app_label = app_label

    token = models.JSONField(
        verbose_name=_("凭据"),
        default={}
    )

    app = models.ForeignKey(
        App,
        verbose_name=_("应用"),
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        verbose_name=_("用户"),
        on_delete=models.CASCADE
    )

class AppMultiAccountSetting(models.Model):
    class Meta:
        app_label = app_label

    bind_url = models.URLField(
        verbose_name=_("绑定接口"),
    )

    unbind_url = models.URLField(
        verbose_name=_("解绑接口")
    )

    app = models.OneToOneField(
        App,
        verbose_name=_("应用"),
        on_delete=models.CASCADE
    )

    username = models.CharField(
        verbose_name=_("用户名"),
        max_length=100
    )