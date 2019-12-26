'''
views for organization
'''

# pylint: disable=no-self-use, invalid-name, unused-argument

from uuid import uuid4

from rest_framework.exceptions import ParseError, NotFound
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ValidationError
from oneid.permissions import (IsAdminUser, IsAuthenticated, IsOrgOwnerOf)
from oneid_meta.models import Dept, Group, Org, GroupMember
from siteapi.v1.serializers.org import OrgSerializer, OrgDeserializer


class OrgListCreateAPIView(GenericAPIView):
    '''
    管理员 检视组织 [GET]
    登录用户 创建组织 [POST]
    '''

    read_permission_classes = [IsAuthenticated & IsAdminUser]
    write_permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        GET org list
        '''
        return Response([OrgSerializer(o).data for o in Org.valid_objects.all()])

    def post(self, request):
        '''
        POST create org
        '''
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

        GroupMember.valid_objects.create(user=self.request.user, owner=manager)
        org = Org.valid_objects.create(name=name,
                                       owner=self.request.user,
                                       dept=dept,
                                       group=group,
                                       direct=direct,
                                       manager=manager,
                                       role=role,
                                       label=label)

        return Response(OrgSerializer(org).data)

    def get_permissions(self):
        '''
        set permissions
        '''
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
    def get(self, request, oid):
        '''
        get org members
        '''
        org = validity_check(oid)
        return Response(collect_org_user(org))

    def get_permissions(self):
        '''
        set permissions
        '''
        IsOrgOwner = IsOrgOwnerOf(validity_check(self.kwargs['oid']))
        permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwner)]
        return [perm() for perm in permission_classes]


class OrgDetailDestroyAPIView(GenericAPIView):
    '''
    组织详情查询 [GET]
    组织删除 [DELETE]
    '''
    read_permission_classes = [IsAuthenticated]

    def get(self, request, oid):
        '''
        org detail view
        '''
        org = validity_check(oid)
        return Response(OrgSerializer(org).data)

    def delete(self, request, oid):
        '''
        delete org
        '''
        org = validity_check(oid)

        org.dept.delete()
        org.group.delete()
        org.direct.delete()
        org.manager.delete()
        org.role.delete()
        org.label.delete()
        org.delete()

        return Response(status=204)

    def get_permissions(self):
        '''
        set permissions
        '''
        method = self.request.method
        if method == 'GET':
            return [perm() for perm in self.read_permission_classes]
        if method == 'DELETE':
            IsOrgOwner = IsOrgOwnerOf(validity_check(self.kwargs['oid']))
            permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwner)]
            return [perm() for perm in permission_classes]
        return []


class UcenterOrgListAPIView(GenericAPIView):
    '''
    个人所属组织列表查询 [GET]
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        get user org list
        '''
        orgs = set()

        def traverse_group(g):
            for org in Org.valid_objects.filter(group=g):
                orgs.add(org)
                return
            if g.parent is not None:
                traverse_group(g.parent)

        for node in GroupMember.valid_objects.filter(user=self.request.user):
            traverse_group(node.owner)

        return Response(map(lambda o: OrgSerializer(o).data, orgs))


class UcenterOwnOrgListAPIView(GenericAPIView):
    '''
    个人拥有组织列表查询 [GET]
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        get user owned org list
        '''
        orgs = set()

        for org in Org.valid_objects.filter(owner=self.request.user):
            orgs.add(org)
        return Response(map(lambda o: OrgSerializer(o).data, orgs))


class UcenterCurrentOrgAPIView(GenericAPIView):
    '''
    个人当前组织查询/切换 [GET] [POST] [DELETE]
    '''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        '''
        get user current org
        '''
        org = self.request.user.current_organization
        if org is not None:
            return Response(OrgSerializer(org).data)
        return Response()    # 这里应该返回什么？

    def delete(self, request):
        '''
        clear user current org
        '''
        self.request.user.current_organization = None
        self.request.user.save()
        return Response(status=204)

    def post(self, request):
        '''
        change user current org
        '''
        try:
            oid = request.data['oid']
        except KeyError:
            raise ParseError()
        org = validity_check(oid)
        self.request.user.current_organization = org
        self.request.user.save()
        return Response(status=204)


def validity_check(oid):
    '''
    check oid
    '''
    try:
        org = Org.valid_objects.filter(uuid=Org.to_uuid(oid))
        if org.exists():
            return org.first()
        raise NotFound
    except ValidationError as exc:
        raise ParseError(exc.messages)


def collect_org_user(org):
    '''
    collect all users in a org
    '''
    users = {org.owner.username}

    def traverse_dept(dept):
        nonlocal users
        users.update({users.username for users in dept.users})
        for d in dept.depts:
            traverse_dept(d)

    def traverse_group(group):
        nonlocal users
        users.update({users.username for users in group.users})
        for g in group.groups:
            traverse_group(g)

    traverse_dept(org.dept)
    traverse_group(org.group)
    return users
