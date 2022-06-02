from posixpath import split
from django.db import models
from arkid.common.model import BaseModel
from arkid.core.translation import gettext_default as _


class Extension(BaseModel):

    class Meta(object):
        verbose_name = _("插件")
        verbose_name_plural = _("插件")

    type = models.CharField(max_length=64, default="base", verbose_name=_('类型'))
    labels = models.JSONField(blank=True, default=[], verbose_name=_('Labels','标签'))
    package = models.CharField(max_length=128, verbose_name=_('标识'), unique=True, db_index=True)
    ext_dir = models.CharField(max_length=1024, verbose_name=_('完整路径名'))
    name = models.CharField(max_length=128, verbose_name=_('名称'))
    version = models.CharField(max_length=128, verbose_name=_('版本'))
    is_active = models.BooleanField(default=False, verbose_name=_('是否启动'))
    profile = models.JSONField(blank=True, default={}, verbose_name=_('Setup Profile','启动设置'))
    is_allow_use_platform_config = models.BooleanField(default=False, verbose_name=_('是否允许租户使用平台配置'))
    

class TenantExtension(BaseModel):
    class Meta(object):
        verbose_name = _("插件租户配置")
        verbose_name_plural = _("插件租户配置")
        unique_together=(('tenant','extension'),)
        
    tenant = models.ForeignKey('core.Tenant', blank=False, on_delete=models.PROTECT, verbose_name=_('租户'))
    extension = models.ForeignKey('Extension', blank=False, on_delete=models.PROTECT, verbose_name=_('插件'))
    settings = models.JSONField(blank=True, default=dict, verbose_name=_('Tenant Settings','租户配置'))
    is_active = models.BooleanField(default=False, verbose_name=_('是否使用'))
    # 如果启用平台配置，运行时，平台租户的配置将会被允许该租户使用，而本身的配置变得无效
    use_platform_config = models.BooleanField(default=False, verbose_name=_('是否使用平台配置'))


class TenantExtensionConfig(BaseModel):

    class Meta(object):
        verbose_name = _("插件运行时配置")
        verbose_name_plural = _("插件运行时配置")

    tenant = models.ForeignKey('core.Tenant', blank=False, on_delete=models.PROTECT, verbose_name=_('租户'))
    extension = models.ForeignKey('Extension', blank=False, on_delete=models.PROTECT, verbose_name=_('插件'))
    config = models.JSONField(blank=True, default=dict, verbose_name=_('Runtime Config','运行时配置'))
    name = models.CharField(max_length=128, default='', verbose_name=_('名称'))
    type = models.CharField(max_length=128, default='', verbose_name=_('类型'))
