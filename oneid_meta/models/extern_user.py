'''
其他网站用户注册表
'''
from django.db import models
from common.django.model import BaseModel
from .user import User


class DingUser(BaseModel):
    '''
    钉钉用户
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='ding_user', on_delete=models.PROTECT)
    account = models.CharField(max_length=64, blank=False, verbose_name='钉钉账号(手机)')
    uid = models.CharField(max_length=255, blank=False, verbose_name='员工在企业内的唯一标识')
    data = models.TextField(blank=True, default='{}', verbose_name='钉钉员工详细数据(JSON)')
    ding_id = models.TextField(max_length=255, blank=True, verbose_name='钉钉ID')
    open_id = models.TextField(max_length=255, blank=True, verbose_name='用户在当前开放应用内的唯一标识')
    union_id = models.TextField(max_length=255, blank=True, verbose_name='用户在当前开放应用所属的钉钉开放平台账号内的唯一标识')


class AlipayUser(BaseModel):
    '''
    支付宝用户
    '''
    user = models.OneToOneField(User, verbose_name='用户', related_name='alipay_user', on_delete=models.PROTECT)
    alipay_id = models.TextField(max_length=255, blank=True, verbose_name='支付宝ID')
