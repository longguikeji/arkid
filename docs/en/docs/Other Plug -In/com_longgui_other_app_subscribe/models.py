from django.db import models
from arkid.core.models import App, User
from django.apps import AppConfig

app_label = "com_longgui_other_app_subscribe"


class LongguiAppSubscribeAppConfig(AppConfig):

    name = app_label

class AppSubscribeRecord(models.Model):
    
    class Meta:
        app_label = app_label
    
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="subscribe_records"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="app_subscribe_records"
    )