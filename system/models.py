from django.db import models
from common.model import BaseModel


class SystemConfig(BaseModel):

    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return str(self.uuid)
