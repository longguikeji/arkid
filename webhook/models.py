from django.db import models
from common.model import BaseModel
from tenant.models import Tenant


class Webhook(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    secret = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name


class WebhookEvent(BaseModel):
    webhook = models.ForeignKey(
        Webhook, related_name="events", on_delete=models.CASCADE
    )
    event_type = models.CharField("Event type", max_length=128, db_index=True)

    def __repr__(self):
        return self.event_type


class WebhookTriggerHistory(BaseModel):

    STATUS_CHOICES = (
        ('waiting', '等待发送'),
        ('success', '发送成功'),
        ('failed', '发送异常'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    webhook = models.ForeignKey(Webhook, on_delete=models.PROTECT)
    status = models.CharField(choices=STATUS_CHOICES, max_length=128, default='waiting')
    request = models.TextField(null=True)  # Headers, Body/Payload ...
    response = models.TextField(null=True)  # Headers, StatusCode, Body ...
