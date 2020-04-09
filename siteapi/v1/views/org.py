'''
views for organization
'''

# pylint: disable=no-self-use, invalid-name, unused-argument, attribute-defined-outside-init, cyclic-import

from rest_framework.exceptions import ParseError, NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework import generics, status, mixins
from rest_framework.exceptions import ValidationError
from django.core import exceptions as django_exceptions
from oneid.permissions import IsAdminUser, IsAuthenticated, IsOrgOwnerOf, IsOrgMember, UserManagerReadable
from oneid_meta.models import Org, User, OrgMember
from siteapi.v1.serializers.user import OrgUserSerializer, OrgUserDeserializer
from siteapi.v1.serializers.org import OrgSerializer, OrgDeserializer
from common.django.drf.paginator import DefaultListPaginator


class OrgListCreateAPIView(generics.ListCreateAPIView):
    '''
    面向普通用户
    - 查看自己所属组织 [GET]
        - 创建的
        - 加入他人的
    - 创建组织 [POST]
    '''
    permission_classes = [IsAuthenticated]
    serializer_class = OrgSerializer

    def get(self, request, *args, **kwargs):
        '''
        查看自己所属组织：
        - 创建的
        - 加入他人的
        '''
        items = self.request.user.organizations
        role = self.request.query_params.get('role', '')
        res = OrgSerializer(items, many=True).data
        if role:
            res = [item for item in res if item['role'] == role]
        return Response(res)

    def post(self, request, *args, **kwargs):
        '''
        创建组织
        '''
        serializer = OrgDeserializer(data=request.data)
        serializer.context['request'] = request
        serializer.is_valid(raise_exception=True)
        org = serializer.save()

        user = request.user
        org.add_member(user)
        user.switch_org(org)
        return Response(OrgSerializer(org).data, status=status.HTTP_201_CREATED)


class OrgDetailAPIView(generics.GenericAPIView):
    '''
    组织详情查询 [GET]
    组织详情更改 [PATCH]
    组织删除 [DELETE]
    '''
    read_permission_classes = [IsAuthenticated]

    def get(self, request, **kw):
        '''
        org detail view
        '''
        return Response(OrgSerializer(self.org).data)

    def patch(self, request, **kw):
        '''
        org info update
        '''
        parse = OrgDeserializer(data=request.data)
        parse.is_valid(raise_exception=True)
        name = parse.validated_data.get('name')
        owner = parse.validated_data.get('owner')
        if name:
            self.org.name = name
            self.org.save()
        if owner:    # TODO： 是否要更严谨的确认过程
            user = User.valid_objects.filter(username=owner).first()
            if not user:
                raise ValidationError
            self.org.owner = user
            self.org.save()
        return Response(OrgSerializer(self.org).data)

    def delete(self, request, **kw):
        '''
        delete org
        '''
        self.org.delete()
        return Response(status=204)

    def get_permissions(self):
        '''
        set permissions
        '''
        self.org = validity_check(self.kwargs['oid'])

        method = self.request.method
        if method == 'GET':
            # TODO: 能否看到自己不在的组织的信息
            return [perm() for perm in self.read_permission_classes]
        if method in ('DELETE', 'PATCH', 'PUT'):
            IsOrgOwner = IsOrgOwnerOf(self.org)
            permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwner)]
            return [perm() for perm in permission_classes]
        return []


class OrgUserListUpdateAPIView(mixins.UpdateModelMixin, generics.ListAPIView):
    '''
    组织成员列表
    - 查询 [GET]
    - 修改: 删除、添加 [PATCH]
    '''

    pagination_class = DefaultListPaginator
    serializer_class = OrgUserSerializer

    def get(self, request, *args, **kwargs):
        '''
        get org members
        '''
        queryset = OrgMember.valid_objects.filter(owner=self.org)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def patch(self, request, *args, **kwargs):
        '''
        编辑成员列表
        - 批量删除
        - 批量添加
        '''
        usernames = request.data.get('usernames', [])
        subject = request.data.get('subject', '')
        if not usernames:
            raise ValidationError({'usernames': ['required']})
        if not subject:
            raise ValidationError({'subject': ['required']})
        if subject not in ['add', 'delete']:
            raise ValidationError({'subject': ['must be one of `add` or `delete`']})

        users = set()
        for username in usernames:
            user = User.valid_objects.filter(username=username).first()
            if not user:
                raise ValidationError({'usernames': [f'valid: {username}']})
            if username == self.org.owner.username:
                raise ValidationError({'usernames': [f'protected: {username}']})
            users.add(user)
        for user in users:
            if subject == 'add':
                self.org.add_member(user)
            elif subject == 'delete':
                self.org.remove_member(user)

        return Response({'username': usernames, 'subject': subject})

    def get_permissions(self):
        '''
        set permissions
        '''
        self.org = validity_check(self.kwargs['oid'])

        IsOrgOwner = IsOrgOwnerOf(self.org)
        permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwner)]    # TODO@saas: OrgMgr?
        return [perm() for perm in permission_classes]


class OrgUserDetailAPIView(generics.RetrieveUpdateAPIView):
    '''
    组织拥有者查看他人信息 [GET] [PATCH]
    '''

    serializer_class = OrgUserSerializer

    def get_permissions(self):
        '''
        set permissions
        '''

        self.org = validity_check(self.kwargs['oid'])
        read_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgMember(self.org) | UserManagerReadable)]
        write_permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwnerOf(self.org) | UserManagerReadable)]

        method = self.request.method
        if method == 'GET':
            return [perm() for perm in read_permission_classes]
        return [perm() for perm in write_permission_classes]

    def get_object(self):
        '''
        find user
        :rtype: oneid_meta.models.User
        '''
        user = User.valid_objects.filter(username=self.kwargs['username']).first()
        if not user:
            raise NotFound
        om = OrgMember.valid_objects.filter(user=user, owner=self.org).first()
        if not om:
            raise NotFound
        try:
            self.check_object_permissions(self.request, user)
        except PermissionDenied:
            raise NotFound

        return om

    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        '''
        update user
        '''
        serializer = OrgUserDeserializer(self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        om = serializer.save()
        return Response(OrgUserSerializer(om).data)


class UcenterCurrentOrgAPIView(generics.GenericAPIView):
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
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        '''
        clear user current org
        '''
        self.request.user.current_organization = None
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request):
        '''
        change user current org
        '''
        oid = request.data.get('oid', '')
        user = self.request.user
        org = Org.valid_objects.filter(uuid=oid).first()
        if not org or not org.has_user(request.user):
            raise ValidationError({'oid': 'invalid'})
        user.current_organization = org
        user.save()
        return Response(OrgSerializer(org).data, status=status.HTTP_200_OK)


def validity_check(oid):
    '''
    check oid
    '''
    try:
        org = Org.valid_objects.filter(uuid=Org.to_uuid(oid))
        if org.exists():
            return org.first()
        raise NotFound
    except django_exceptions.ValidationError as exc:
        raise ParseError(exc.messages)
