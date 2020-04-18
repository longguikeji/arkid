'''
model for advanced feature
'''

from django.db import models

from common.django.model import BaseModel


class Plugin(BaseModel):
    '''
    自定义插件
    '''
    class Meta:    # pylint: disable=missing-docstring
        abstract = True

    name = models.CharField(max_length=255, verbose_name='插件名称')
    detail = models.CharField(max_length=1024, verbose_name='插件详细描述')
    import_path = models.CharField(max_length=1024, verbose_name='插件实现所在路径')


class CrontabPlugin(Plugin):
    '''
    周期性任务
    '''
    schedule = models.CharField(max_length=255, verbose_name='执行周期')


class MiddlewarePlugin(Plugin):
    '''
    中间件
    '''

    order_no = models.IntegerField(default=0, verbose_name='排序号')
