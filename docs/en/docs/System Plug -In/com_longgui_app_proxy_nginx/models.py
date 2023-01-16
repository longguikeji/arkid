from django.db import models
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import AppExpandAbstract

app_label = "com_longgui_app_proxy_nginx"


class LongguiAppProxyNginxAppConfig(AppConfig):
    name = app_label


class NginxAPP(AppExpandAbstract):
    class Meta:
        app_label = app_label

    is_intranet_url = models.BooleanField(
        default=False, verbose_name=_('Is Intranet URL', '是否内网地址')
    )
    nginx_config_created = models.BooleanField(
        default=False, verbose_name=_('Nginx config created', '是否已经创建nginx配置')
    )
    nginx_config_deleted = models.BooleanField(
        default=False, verbose_name=_('Nginx config deleted', '是否已经删除nginx配置')
    )
