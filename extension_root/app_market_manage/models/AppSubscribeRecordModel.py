from django.db import models
from django.utils.translation import ugettext_lazy as _
from app.models import App
from common.model import BaseModel
from django.contrib.auth import get_user_model
User = get_user_model()

class AppSubscribeRecord(BaseModel):
    
    app = models.OneToOneField(
        App,
        verbose_name=_("应用"),
        on_delete=models.PROTECT,
        related_name="subscribed_record"
    )

    users = models.ManyToManyField(
        User,
        related_name="app_subscribed_records",
        verbose_name=_("订阅用户")
    )

    class Meta:
        verbose_name = _("应用订阅记录")