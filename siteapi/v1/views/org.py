'''
views for organization
'''

# pylint: disable=no-self-use, invalid-name, unused-argument

from uuid import uuid4

from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ValidationError
from oneid.permissions import (IsAdminUser, IsAuthenticated)
from oneid_meta.models import Dept, Group, Org
from siteapi.v1.serializers.org import OrgSerializer, OrgDeserializer


class OrgListCreateAPIView(GenericAPIView):
    '''
    管理员 检视组织 [GET]
    登录用户 创建组织 [POST]
    '''

    read_permission_classes = [IsAuthenticated & IsAdminUser]
    write_permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([OrgSerializer(o).data for o in Org.valid_objects.all()])

    def post(self, request):
        parse = OrgDeserializer(data=request.data)
        parse.is_valid(raise_exception=True)

        name = parse.validated_data['name']

        dept_root = Dept.valid_objects.filter(uid='root').first()
        group_root = Group.valid_objects.filter(uid='root').first()

        dept = Dept.valid_objects.create(uid=uuid4(), name=name, parent=dept_root)
        group = Group.valid_objects.create(uid=uuid4(), name=name, parent=group_root)
        direct = Group.valid_objects.create(uid=uuid4(), name=f'{name}-无分组成员', parent=group)
        manager = Group.valid_objects.create(uid=uuid4(), name=f'{name}-管理员', parent=group)
        role = Group.valid_objects.create(uid=uuid4(), name=f'{name}-角色', parent=group)
        label = Group.valid_objects.create(uid=uuid4(), name=f'{name}-标签', parent=group)

        org = Org.valid_objects.create(name=name,
                                       dept=dept,
                                       group=group,
                                       direct=direct,
                                       manager=manager,
                                       role=role,
                                       label=label)

        return Response(OrgSerializer(org).data)

    def get_permissions(self):
        method = self.request.method
        if method == 'POST':
            return [perm() for perm in self.write_permission_classes]
        if method == 'GET':
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
            org = Org.valid_objects.filter(uuid=Org.to_uuid(oid))
            if org.exists():
                return org
            raise NotFound
        except ValidationError as exc:
            raise ParseError(exc.messages)

    def get(self, request, **kwargs):
        org = self.validity_check(kwargs['oid'])
        org = org.first()

        users = set()

        def traverse_dept(dept):
            nonlocal users
            users = users.union({users.uid for users in dept.users})
            for d in dept.depts:
                traverse_dept(d)

        def traverse_group(group):
            nonlocal users
            users = users.union({users.uid for users in group.users})
            for g in group.groups:
                traverse_group(g)

        traverse_dept(org.dept)
        traverse_group(org.group)
        return Response(users)


class OrgDetailDestroyAPIView(GenericAPIView):
    '''
    组织详情查询 [GET]
    组织删除 [DELETE]
    '''
    read_permission_classes = [IsAuthenticated]    # TODO
    write_permission_classes = [IsAuthenticated]    # TODO

    @staticmethod
    def validity_check(oid):
        try:
            org = Org.valid_objects.filter(uuid=Org.to_uuid(oid))
            if org.exists():
                return org
            raise NotFound
        except ValidationError as exc:
            raise ParseError(exc.messages)

    def get(self, request, **kwargs):
        org = self.validity_check(kwargs['oid'])
        return Response(OrgSerializer(org.first()).data)

    def delete(self, request, **kwargs):
        org = self.validity_check(kwargs['oid']).first()

        org.dept.delete()
        org.group.delete()
        org.direct.delete()
        org.manager.delete()
        org.role.delete()
        org.label.delete()
        org.delete()

        return Response(status=204)

    def get_permissions(self):
        method = self.request.method
        if method == 'POST':
            return [perm() for perm in self.write_permission_classes]
        if method == 'GET':
            return [perm() for perm in self.read_permission_classes]
        return []
