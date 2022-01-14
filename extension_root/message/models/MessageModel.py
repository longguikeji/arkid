"""
认证规则
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _
from app.models import App
from common.model import BaseModel
from django.contrib.auth import get_user_model
User = get_user_model()


class Message(BaseModel):

    app = models.ForeignKey(
        App,
        on_delete=models.SET_NULL,
        verbose_name=_('来源应用'),
        related_name="messages",
        null=True
    )

    title = models.CharField(
        verbose_name=_('标题'),
        max_length=128,
        default='',
        null=True,
        blank=True
    )

    time = models.DateTimeField(
        verbose_name=_("时间"),
        auto_now_add=True,
    )

    content = models.TextField(
        verbose_name=_("内容")
    )

    users = models.ManyToManyField(
        User,
        verbose_name=_("关联用户"),
        related_name="messages",
        null=True
    )
    
    url = models.URLField(
        verbose_name=_("链接"),
        blank=True,
        null=True
    )
    
    type = models.CharField(
        verbose_name=_("类别"),
        max_length=100,
        help_text=_("支持的分类有notice通知,ticket工单，announcement公告")
    )

    class Meta:
        verbose_name = _("消息")
