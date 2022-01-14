from django.db import models
from django.utils.translation import ugettext_lazy as _
from app.models import App
from inventory.models import User
from common.model import BaseModel


class AppAccount(BaseModel):

    app = models.ForeignKey(
        App, on_delete=models.PROTECT, verbose_name=_('应用'), related_name="app_accounts"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("关联用户"),
        related_name="app_accounts",
    )

    username = models.CharField(verbose_name="用户名", max_length=128)
    password = models.CharField(verbose_name="密码", max_length=128)

    class Meta:
        app_label = 'auto_form_fill'
