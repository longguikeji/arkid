from django.db import models
from common.model import BaseModel

class Device(BaseModel):

    device_type = models.CharField(verbose_name='设备类型', max_length=128, default='', null=True, blank=True)
    system_version = models.CharField(verbose_name='操作系统及版本', max_length=216, default='', null=True, blank=True)
    browser_version = models.CharField(verbose_name='浏览器及版本', max_length=216, default='', null=True, blank=True)
    ip = models.CharField(verbose_name='IP地址', max_length=216, default='', null=True, blank=True)
    mac_address = models.CharField(verbose_name='mac地址', max_length=216, default='', null=True, blank=True)
    device_number = models.CharField(verbose_name='设备号', max_length=216, default='', null=True, blank=True)
    device_id = models.CharField(verbose_name='设备编号', max_length=216, default='', null=True, blank=True)
    account_ids = models.JSONField(verbose_name='用户账号ID', blank=True, default=dict)

    def __str__(self) -> str:
        return self.uuid_hex
