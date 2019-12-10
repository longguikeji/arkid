'''
views for organization
'''

from uuid import uuid4

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
    登录用户 创建/删除组织 [POST] [DELETE]
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
        dept.save()

        group = Group.objects.create(uid=uuid4(), name=name, parent=group_root)
        group.save()

        direct = Group.objects.create(uid=uuid4(), name='无分组成员', parent=group)
        direct.save()

        manager = Group.objects.create(uid=uuid4(), name='管理员', parent=group)
        manager.save()

        role = Group.objects.create(uid=uuid4(), name='角色', parent=group)
        role.save()

        label = Group.objects.create(uid=uuid4(), name='标签', parent=group)
        label.save()

        org = Org.objects.create(
            name=name,
            dept_uid=dept,
            group_uid=group,
            direct_uid=direct,
            manager_uid=manager,
            role_uid=role,
            label_uid=label
        )
        org.save()

        return Response(org_ser(org))

    def get_permissions(self):
        method = self.request.method
        if (method == 'POST'):
            return [perm() for perm in self.write_permission_classes]
        elif (method == 'GET'):
            return [perm() for perm in self.read_permission_classes]
        return []

class OrgUserListAPIView(GenericAPIView):
    '''
    组织成员列表 [GET]
    '''
    permission_classes = [IsAuthenticated & IsAdminUser]
    # permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgMember)]

    def get(self, request, *args, **kwargs):
        u = []

        from oneid_meta.models import User, DeptMember

        oid = kwargs['oid']
        org = Org.valid_objects.filter(uuid=Org.to_uuid(oid)).first()
        dept = org.dept_uid
        group = org.group_uid

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

        traverse_dept(dept)
        traverse_group(group)
        return Response(u)

class OrgDetailDestroyAPIView(GenericAPIView):
    '''
    组织详情查询 [GET]
    组织删除 [DELETE]
    '''
    read_permission_classes = [IsAuthenticated] # TODO
    write_permission_classes = [IsAuthenticated] # TODO

    def get(self, request, *args, **kwargs):
        oid = kwargs['oid']
        return Response(org_ser(Org.valid_objects.filter(uuid=Org.to_uuid(oid)).first()))

    def delete(self, request, *args, **kwargs):
        oid = kwargs['oid']
        org = Org.valid_objects.filter(uuid=Org.to_uuid(oid)).first()

        org.dept_uid.delete()
        org.group_uid.delete()
        org.direct_uid.delete()
        org.manager_uid.delete()
        org.role_uid.delete()
        org.label_uid.delete()
        org.delete()
        org.save()

        return Response()

    def get_permissions(self):
        method = self.request.method
        if (method == 'POST'):
            return [perm() for perm in self.write_permission_classes]
        elif (method == 'GET'):
            return [perm() for perm in self.read_permission_classes]
        return []


def org_ser(org):
    ret = {}

    ret['oid'] = org.uuid
    ret['name'] = org.name
    ret['dept_uid'] = org.dept_uid.uid
    ret['group_uid'] = org.group_uid.uid
    ret['direct_uid'] = org.group_uid.uid
    ret['manager_uid'] = org.manager_uid.uid
    ret['role_uid'] = org.role_uid.uid
    ret['label_uid'] = org.label_uid.uid

    return ret

