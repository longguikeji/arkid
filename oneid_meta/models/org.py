'''
schema of Orgs
'''
# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=no-member
from uuid import uuid4
from django.db import models
from django.utils import timezone
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
    app_group = models.ForeignKey('oneid_meta.AppGroup', on_delete=models.CASCADE, verbose_name='App分组节点')
    default_app_group = models.ForeignKey('oneid_meta.AppGroup',
                                          on_delete=models.CASCADE,
                                          verbose_name='App分组默认节点',
                                          related_name='default_app')
    role = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='角色节点', related_name='role')
    label = models.ForeignKey('oneid_meta.Group', on_delete=models.CASCADE, verbose_name='标签节点', related_name='label')

    @property
    def oid(self):
        '''
        get oid
        TODO: refactor: oid 应该为 string 类型
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
        self.app_group.delete()
        self.default_app_group.delete()
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
        from oneid_meta.models import Perm, Dept, Group, GroupMember, CompanyConfig, AppGroup

        dept_root = Dept.valid_objects.filter(uid='root').first()
        group_root = Group.valid_objects.filter(uid='root').first()
        app_group_root = AppGroup.valid_objects.filter(uid='root').first()

        dept = Dept.valid_objects.create(uid=str(uuid4()), name=name, parent=dept_root)
        group = Group.valid_objects.create(uid=str(uuid4()), name=name, parent=group_root)
        app_group = AppGroup.valid_objects.create(uid=str(uuid4()), name=f'{name}-应用', parent=app_group_root)
        direct = Group.valid_objects.create(uid=str(uuid4()), name=f'{name}-直属成员', parent=group)
        manager = Group.valid_objects.create(uid=str(uuid4()), name=f'{name}-管理员', parent=group)
        default_app_group = AppGroup.valid_objects.create(uid=str(uuid4()), name=f'{name}-默认应用', parent=app_group)
        role = Group.valid_objects.create(uid=str(uuid4()), name=f'{name}-角色', parent=group)
        label = Group.valid_objects.create(uid=str(uuid4()), name=f'{name}-标签', parent=group)

        group.top = group.uid
        direct.top = direct.uid
        manager.top = manager.uid
        app_group.top = app_group.uid
        default_app_group.top = default_app_group.uid
        role.top = role.uid
        label.top = label.uid

        group.save()
        direct.save()
        manager.save()
        app_group.save()
        default_app_group.save()
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
            'app_group': app_group,
            'default_app_group': default_app_group,
            'role': role,
            'label': label
        }

        try:
            kw['uuid'] = kwargs['uuid']
        except KeyError:
            pass

        org = Org.valid_objects.create(**kw)

        OrgMember.valid_objects.create(user=owner, owner=org)
        owner.current_organization = org
        owner.save(update_fields=['current_organization'])
        CompanyConfig.objects.create(org=org)

        oid = org.oid_str
        Perm.objects.create(name='创建大类', uid=f'{oid}_category_create', subject=oid, scope='category', action='create')
        Perm.objects.create(name='创建应用', uid=f'{oid}_app_create', subject=oid, scope='app', action='create')
        Perm.objects.create(name='查看日志', uid=f'{oid}_log_read', subject=oid, scope='log', action='read')
        Perm.objects.create(name='公司基本信息配置、基础设施配置',
                            uid=f'{oid}_config_write',
                            subject=oid,
                            scope='config',
                            action='write')
        Perm.objects.create(name='账号同步', uid=f'{oid}_account_sync', subject=oid, scope='account', action='sync')
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

    def remove_member(self, user):
        '''
        remove user from org
        '''
        # pylint: disable=import-outside-toplevel
        from oneid_meta.models import GroupMember, DeptMember

        for gm in GroupMember.valid_objects.filter(user=user):
            org = gm.owner.org
            if org and org.uuid == self.uuid:
                gm.kill()
        for dm in DeptMember.valid_objects.filter(user=user):
            org = dm.owner.org
            if org and org.uuid == self.uuid:
                dm.kill()
        om = OrgMember.valid_objects.filter(user=user, owner=self).first()
        if om:
            om.kill()

    def add_member(self, user):
        '''
        将 user 加入到组织
        不负责更具体的 node的加入 -> TODO: 需要负责
        '''
        org_member, created = OrgMember.valid_objects.get_or_create(user=user, owner=self)
        if created:
            org_member.hiredate = timezone.now()

    def get_user_role(self, user):
        '''
        获取 user 在该组织中的角色，互斥
        - owner - 管理员，创建者
        - manager - 子管理员
        - member - 普通成员
        - "" - 不属于该组织
        '''
        if user == self.owner:
            return 'owner'

        org_member = OrgMember.valid_objects.filter(user=user, owner=self).first()
        if not org_member:
            return ""
        if org_member.is_manager:
            return "manager"
        return "member"

    def has_user(self, user):
        '''
        判断一个用户是否属于该组织
        '''
        return OrgMember.valid_objects.filter(user=user, owner=self).exists()


class OrgMember(BaseOrderedModel):
    '''
    组织与用户的关系
    - 记录用户在组织内部特有的信息
    - 记录组织与用户的从属关系，会作为用户是否属于某组织的直接判断依据。-> 注意维护
    '''

    user = models.ForeignKey('oneid_meta.User', on_delete=models.PROTECT)
    owner = models.ForeignKey(Org, verbose_name='所属组织', on_delete=models.PROTECT)
    employee_number = models.CharField(max_length=255, blank=True, default='', verbose_name='工号')
    position = models.CharField(max_length=255, blank=True, default='', verbose_name='职位')
    hiredate = models.DateTimeField(blank=True, null=True, verbose_name='入职时间')
    remark = models.CharField(max_length=512, blank=True, default='', verbose_name='备注')
    email = models.CharField(max_length=255, blank=True, default='', verbose_name='企业邮箱')

    class Meta:    # pylint: disable=missing-docstring
        unique_together = ('user', 'owner')

    def __str__(self):
        return f'OrgMember: {self.user} -> {self.owner}'

    @property
    def nodes(self):
        '''
        此人在此组织所处node
        '''
        yield from self.depts
        yield from self.groups

    @property
    def depts(self):
        '''
        此人在此组织所处部门
        '''
        for item in self.user.depts:
            if item.org == self.owner:
                yield item

    @property
    def groups(self):
        '''
        此人在此组织所处组
        '''
        for item in self.user.groups:
            if item.org == self.owner:
                yield item

    @property
    def is_manager(self):
        '''
        此人在此组织是否为子管理员
        '''
        from oneid_meta.models import GroupMember    # pylint: disable=import-outside-toplevel
        return GroupMember.valid_objects.filter(user=self.user, owner__parent=self.owner.manager).exists()
