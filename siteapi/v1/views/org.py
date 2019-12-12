'''
views for organization
'''

from uuid import uuid4

from django.core.exceptions import ValidationError
from rest_framework.exceptions import ParseError, NotFound

from rest_framework.response import Response
from rest_framework.generics import *
from oneid.permissions import (
    IsAdminUser,
    IsAuthenticated
)
from oneid_meta.models.dept import Dept
from oneid_meta.models.group import Group
from oneid_meta.models.org import Org


class OrgListCreateAPIView(GenericAPIView):
    '''
    管理员 检视组织 [GET]
    登录用户 创建组织 [POST]
    '''

    read_permission_classes = [IsAuthenticated & IsAdminUser]
    write_permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([org_ser(o) for o in Org.valid_objects.all()])

    def post(self, request):
        name=request.data['name']

        dept_root = Dept.objects.filter(uid='root').first()
        group_root = Group.objects.filter(uid='root').first()

        dept = Dept.objects.create(uid=uuid4(), name=name, parent=dept_root)
        group = Group.objects.create(uid=uuid4(), name=name, parent=group_root)
        direct = Group.objects.create(uid=uuid4(), name=f'{name}-无分组成员', parent=group)
        manager = Group.objects.create(uid=uuid4(), name=f'{name}-管理员', parent=group)
        role = Group.objects.create(uid=uuid4(), name=f'{name}-角色', parent=group)
        label = Group.objects.create(uid=uuid4(), name=f'{name}-标签', parent=group)

        org = Org.objects.create(
            name=name,
            dept=dept,
            group=group,
            direct=direct,
            manager=manager,
            role=role,
            label=label
        )

        return Response(org_ser(org))

    def get_permissions(self):
        method = self.request.method
        if method == 'POST':
            return [perm() for perm in self.write_permission_classes]
        elif method == 'GET':
            return [perm() for perm in self.read_permission_classes]
        return []


class OrgUserListAPIView(GenericAPIView):
    '''
    组织成员列表 [GET]
    '''
    permission_classes = [IsAuthenticated & IsAdminUser]
    # permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgMember)]

    @staticmethod
    def validity_check(oid):
        try:
            o = Org.valid_objects.filter(uuid=Org.to_uuid(oid))
            if o.exists():
                return o
            else:
                raise NotFound
        except ValidationError as e:
            raise ParseError(e.messages)

    def get(self, request, *args, **kwargs):
        u = []

        o = self.validity_check(kwargs['oid'])
        org = o.first()

        def traverse_dept(dept):
            nonlocal u
            u += [u.uid for u in dept.users]
            for d in dept.depts:
                traverse_dept(d)

        def traverse_group(group):
            nonlocal u
            u += [u.uid for u in group.users]
            for g in group.groups:
                traverse_group(g)

        traverse_dept(org.dept)
        traverse_group(org.group)
        return Response(u)


class OrgDetailDestroyAPIView(GenericAPIView):
    '''
    组织详情查询 [GET]
    组织删除 [DELETE]
    '''
    read_permission_classes = [IsAuthenticated] # TODO
    write_permission_classes = [IsAuthenticated] # TODO

    @staticmethod
    def validity_check(oid):
        try:
            o = Org.valid_objects.filter(uuid=Org.to_uuid(oid))
            if o.exists():
                return o
            else:
                raise NotFound
        except ValidationError as e:
            raise ParseError(e.messages)

    def get(self, request, *args, **kwargs):
        o = self.validity_check(kwargs['oid'])
        return Response(org_ser(o.first()))

    def delete(self, request, *args, **kwargs):
        o = self.validity_check(kwargs['oid'])
        org = o.first()

        org.dept.delete()
        org.group.delete()
        org.direct.delete()
        org.manager.delete()
        org.role.delete()
        org.label.delete()
        org.delete()

        return Response()

    def get_permissions(self):
        method = self.request.method
        if method == 'POST':
            return [perm() for perm in self.write_permission_classes]
        elif method == 'GET':
            return [perm() for perm in self.read_permission_classes]
        return []


def org_ser(org):
    return {
        'oid': str(org.uuid),
        'name': org.name,
        'dept_uid': org.dept.uid,
        'group_uid': org.group.uid,
        'direct_uid': org.direct.uid,
        'manager_uid': org.manager.uid,
        'role_uid': org.role.uid,
        'label_uid': org.label.uid
    }
