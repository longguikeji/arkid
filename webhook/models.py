from django.db import models
from arkid.core.models import BaseModel, Tenant
from arkid.core.translation import gettext_default as _


class Webhook(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    secret = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return self.name


class WebhookEvent(BaseModel):
    webhooks = models.ManyToManyField(
        Webhook,
        blank=True,
        related_name="events_set",
        related_query_name="events",
    )
    event_type = models.CharField("Event type", max_length=128, db_index=True)

    def __repr__(self):
        return self.event_type


class WebhookTriggerHistory(BaseModel):

    STATUS_CHOICES = (
        ('waiting', _('Waiting', '等待发送')),
        ('success', _('Success', '发送成功')),
        ('failed', _('Failed', '发送异常')),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.PROTECT,
        related_name="history_set",
        related_query_name="histories",
    )
    status = models.CharField(choices=STATUS_CHOICES, max_length=128, default='waiting')
    request = models.TextField(
        blank=True, null=True, verbose_name=_('Http Request', 'Http请求')
    )  # Headers, Body/Payload ...
    response = models.TextField(
        blank=True, null=True, verbose_name=_('Http Response', 'Http返回结果')
    )
