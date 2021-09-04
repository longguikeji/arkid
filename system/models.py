from django.db import models
from common.model import BaseModel


class SystemConfig(BaseModel):

    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return str(self.uuid)


# class SystemPrivacyNotice(BaseModel):

#     title = models.CharField(
#         verbose_name='标题', max_length=128, blank=True, null=True, default=''
#     )
#     content = models.TextField(verbose_name='内容', blank=True, null=True, default='')

#     def __str__(self) -> str:
#         return f'System Privacy Notice: {self.title}'
