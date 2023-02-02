from django.db import models
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.common.model import BaseModel
from arkid.core.models import UserExpandAbstract, UserGroupExpandAbstract, Tenant

app_label = "com_longgui_custom_field"

class LongguiCustomFieldAppConfig(AppConfig):
    name = app_label

class CustomUser(UserExpandAbstract):
    '''
    自定义用户信息
    '''
    class Meta:
        app_label = app_label
    
    data = models.JSONField(
        default={},
        verbose_name=_('内容')
    )

class CustomUserGroup(UserGroupExpandAbstract):
    '''
    自定义分组信息
    '''
    class Meta:
        app_label = app_label
    
    data = models.JSONField(
        default={},
        verbose_name=_('内容')
    )
class CustomField(BaseModel):
    '''
    自定义字段
    '''
    class Meta:
        app_label = app_label

    SUBJECT_CHOICES = (
        ('user', '用户'),
        ('user_group', '组'),
    )

    name = models.CharField(max_length=128, verbose_name=_('字段名称'))
    subject = models.CharField(choices=SUBJECT_CHOICES, default='user', max_length=128, verbose_name=_('字段分类'))
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, verbose_name='租户')
    schema = models.JSONField(
        default={"type": "string"},
        verbose_name=_('字段定义')
    )
    is_visible = models.BooleanField(default=True, verbose_name=_("是否展示"))
