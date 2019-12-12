'''
schema of Orgs
'''

from django.db import models
from common.django.model import BaseModel


class Org(BaseModel):
    '''
    组织信息
    '''
    def __str__(self):
        return f'Organization: {self.oid}({self.name})'

    name = models.CharField(max_length=255, blank=False, verbose_name='组织名')

    dept = models.ForeignKey('oneid_meta.Dept', on_delete=models.CASCADE, verbose_name='部门节点')
    group = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='组节点')

    direct = models.ForeignKey('oneid_meta.Group',
                               on_delete=models.CASCADE,
                               verbose_name='直属成员节点',
                               related_name='direct')
    manager = models.ForeignKey('oneid_meta.Group',
                                on_delete=models.CASCADE,
                                verbose_name='管理员节点',
                                related_name='manager')
    role = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='角色节点', related_name='role')
    label = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='标签节点', related_name='label')

    @property
    def oid(self):
        return self.uuid

    @property
    def oid_str(self):
        return str(self.oid)

    @staticmethod
    def to_uuid(oid):
        return oid
