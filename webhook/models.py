from django.db import models
import jsonfield

from common.model import BaseModel
from tenant.models import Tenant


class WebHook(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    secret = models.CharField(max_length=128, blank=True, null=True)
    content_type = models.CharField(max_length=128, default="application/json")
    events = jsonfield.JSONField()


class WebHookTriggerHistory(BaseModel):

    STATUS_CHOICES = (
        (0, '等待发送'),
        (1, '发送成功'),
        (2, '发送异常'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    webhook = models.ForeignKey(WebHook, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    request = jsonfield.JSONField() # Headers, Body/Payload ...
    response = jsonfield.JSONField() # Headers, StatusCode, Body ...


