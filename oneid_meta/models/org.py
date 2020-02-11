'''
schema of Orgs
'''
# pylint: disable=invalid-name
from uuid import uuid4
from django.db import models
from common.django.model import BaseModel, BaseOrderedModel


class Org(BaseModel):
    '''
    组织信息
    '''
    def __str__(self):
        return f'Organization: {self.oid}({self.name})'

    name = models.CharField(max_length=255, blank=False, verbose_name='组织名')
    owner = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE, verbose_name='所有者')

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
        '''
        get oid
        '''
        return self.uuid

    @property
    def oid_str(self):
        '''
        get string oid
        :return:
        '''
        return str(self.oid)

    @staticmethod
    def to_uuid(oid):
        '''
        convert oid to uuid
        '''
        return oid

    def delete(self):
        # pylint: disable=no-member, arguments-differ
        self.dept.delete()
        self.group.delete()
        self.direct.delete()
        self.manager.delete()
        self.role.delete()
        self.label.delete()
        for om in OrgMember.valid_objects.filter(owner=self):
            om.delete()
        super(Org, self).delete()

    @staticmethod
    def create(name, owner, **kwargs):
        '''
        create org
        '''
        # pylint: disable=too-many-locals,import-outside-toplevel
        from oneid_meta.models import Dept, Group, GroupMember, CompanyConfig

        dept_root = Dept.valid_objects.filter(uid='root').first()
        group_root = Group.valid_objects.filter(uid='root').first()

        dept = Dept.valid_objects.create(uid=uuid4(), name=name, parent=dept_root)
        group = Group.valid_objects.create(uid=uuid4(), name=name, parent=group_root)
        direct = Group.valid_objects.create(uid=uuid4(), name=f'{name}-无分组成员', parent=group)
        manager = Group.valid_objects.create(uid=uuid4(), name=f'{name}-管理员', parent=group)
        role = Group.valid_objects.create(uid=uuid4(), name=f'{name}-角色', parent=group)
        label = Group.valid_objects.create(uid=uuid4(), name=f'{name}-标签', parent=group)

        group.top = group.uid
        direct.top = direct.uid
        manager.top = manager.uid
        role.top = role.uid
        label.top = label.uid

        group.save()
        direct.save()
        manager.save()
        role.save()
        label.save()

        GroupMember.valid_objects.create(user=owner, owner=direct)

        kw = {
            'name': name,
            'owner': owner,
            'dept': dept,
            'group': group,
            'direct': direct,
            'manager': manager,
            'role': role,
            'label': label
        }

        try:
            kw['uuid'] = kwargs['uuid']
        except KeyError:
            pass

        org = Org.valid_objects.create(**kw)
        OrgMember.valid_objects.create(user=owner, owner=org)
        CompanyConfig.objects.create(org=org)
        return org

    @property
    def users(self):
        '''
        org user list
        '''
        def traverse_dept(dept):
            yield from (u.username for u in dept.users)
            for d in dept.depts:
                yield from traverse_dept(d)

        def traverse_group(group):
            yield from (u.username for u in group.users)
            for g in group.groups:
                yield from traverse_group(g)

        yield from traverse_dept(self.dept)
        yield from traverse_group(self.group)

    def remove(self, user):
        '''
        remove user from org
        '''
        # pylint: disable=import-outside-toplevel
        from oneid_meta.models import GroupMember, DeptMember

        for gm in GroupMember.valid_objects.filter(user=user):
            org = gm.owner.org
            if org and org.uuid == self.uuid:
                gm.delete()
        for dm in DeptMember.valid_objects.filter(user=user):
            org = dm.owner.org
            if org and org.uuid == self.uuid:
                dm.delete()


class OrgMember(BaseOrderedModel):
    '''
    组织与用户的从属关系
    这里部门仅收录末端部门
    '''

    user = models.ForeignKey('oneid_meta.User', on_delete=models.PROTECT)
    owner = models.ForeignKey(Org, verbose_name='所属组织', on_delete=models.PROTECT)
    employee_number = models.CharField(max_length=255, blank=True, default='', verbose_name='工号')
    position = models.CharField(max_length=255, blank=True, default='', verbose_name='职位')
    hiredate = models.DateTimeField(blank=True, null=True, verbose_name='入职时间')
    remark = models.CharField(max_length=512, blank=True, default='', verbose_name='备注')

    class Meta:    # pylint: disable=missing-docstring
        unique_together = ('user', 'owner')

    def __str__(self):
        return f'OrgMember: {self.user} -> {self.owner}'
