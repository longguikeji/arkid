from django.db import models
import jsonfield
import base64
import hmac
import random
import string
from hashlib import sha256
from common.model import BaseModel
from tenant.models import Tenant


def random_secret64():
    """Generate random secret (letters, digits, punctuation)."""
    punctuation = string.punctuation.replace('"', '').replace("'", '')
    chars = string.ascii_letters + string.digits + punctuation
    return ''.join(random.choice(chars) for _ in range(64))


class WebHook(BaseModel):

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    secret = models.CharField(
        max_length=128, blank=True, null=True, default=random_secret64
    )
    content_type = models.CharField(max_length=128, default="application/json")
    events = jsonfield.JSONField()

    def as_dict(self):
        return {
            'name': self.name,
            'uuid': str(self.uuid),
            'url': self.url,
            'content_type': self.content_type,
            'secret': self.secret,
        }

    def sign(self, data):
        key = self.secret.encode('utf-8')
        message = data.encode('utf-8')
        sign = base64.b64encode(hmac.new(key, message, digestmod=sha256).digest())
        sign = str(sign, 'utf-8')
        return sign


class WebHookTriggerHistory(BaseModel):

    STATUS_CHOICES = (
        (0, '等待发送'),
        (1, '发送成功'),
        (2, '发送异常'),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    webhook = models.ForeignKey(WebHook, on_delete=models.PROTECT)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    request = jsonfield.JSONField(null=True)  # Headers, Body/Payload ...
    response = jsonfield.JSONField(null=True)  # Headers, StatusCode, Body ...
