'''
schema of Orgs
'''

from django.db import models
from common.django.model import BaseModel

class Org(BaseModel):
    '''
    OID->节点UID查询表
    '''

    def __str__(self):
        return f'Organization: {self.oid}({self.name})'

    name = models.CharField(max_length=255, blank=False, verbose_name='组织名')

    dept_uid = models.ForeignKey('oneid_meta.Dept', on_delete=models.CASCADE, verbose_name='部门节点')
    group_uid = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='组节点')

    direct_uid = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='直属成员节点', related_name='direct_uid')
    manager_uid = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='管理员节点', related_name='manager_uid')
    role_uid = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='角色节点', related_name='role_uid')
    label_uid = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='标签节点', related_name='label_uid')


    @property
    def oid(self):
        return self.uuid

    @staticmethod
    def to_uuid(oid):
        return oid
