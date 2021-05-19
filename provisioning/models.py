from django.db import models
from common.model import BaseModel
from app.models import App
from schema.models import Schema
from .constants import ProvisioningMode, ProvisioningStatus


class Config(BaseModel):

    STATUS_CHOICES = (
        (ProvisioningStatus.Enabled.value, 'Enabled'),
        (ProvisioningStatus.Disabled.value, 'Disabled'),
    )

    MODE_CHOICES = ((ProvisioningMode.Automatic.value, 'Automatic'),)

    app = models.ForeignKey(App, on_delete=models.PROTECT)
    endpoint = models.CharField(max_length=1024, blank=False, null=True)
    token = models.CharField(max_length=256, blank=True, null=True)
    schemas = models.ManyToManyField(Schema, blank=True)

    mode = models.IntegerField(choices=MODE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    def should_provision(self, user):
        return True
