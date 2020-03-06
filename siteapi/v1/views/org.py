'''
views for organization
'''

# pylint: disable=no-self-use, invalid-name, unused-argument, attribute-defined-outside-init, cyclic-import

from rest_framework.exceptions import ParseError, NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ValidationError, RetrieveUpdateAPIView
from oneid.permissions import IsAdminUser, IsAuthenticated, IsOrgOwnerOf, IsOrgMember, UserManagerReadable
from oneid_meta.models import Org, GroupMember, User, OrgMember
from siteapi.v1.serializers.user import OrgUserSerializer, OrgUserDeserializer
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
        return Response(OrgSerializer(Org.create(name=name, owner=self.request.user)).data)

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


class OrgUserListCreateDestroyAPIView(GenericAPIView):
    '''
    组织成员列表/添加/删除 [GET] [POST] [DELETE]
    '''
    def get(self, request, **kw):
        '''
        get org members
        '''
        return Response(self.org.users)

    def post(self, request, **kw):
        '''
        add org members
        '''
        user = request.query_params.get('username', None)
        if user is None:
            raise NotFound
        user = User.valid_objects.filter(username=user)
        if user.exists():
            GroupMember.valid_objects.create(user=user.first(), owner=self.org.direct)
        else:
            raise NotFound
        return Response(status=204)

    def delete(self, request, **kw):
        '''
        delete org members
        '''
        user = request.query_params.get('username', None)
        if user is None:
            raise NotFound
        user = User.valid_objects.filter(username=user)
        if user.exists():
            self.org.remove(user.first())
        else:
            raise NotFound
        return Response(status=204)

    def get_permissions(self):
        '''
        set permissions
        '''
        self.org = validity_check(self.kwargs['oid'])

        IsOrgOwner = IsOrgOwnerOf(self.org)
        permission_classes = [IsAuthenticated & (IsAdminUser | IsOrgOwner)]    # TODO@saas: OrgMgr?
        return [perm() for perm in permission_classes]


class OrgDetailDestroyAPIView(GenericAPIView):
    '''
    组织详情查询 [GET]
    组织删除 [DELETE]
    '''
    read_permission_classes = [IsAuthenticated]

    def get(self, request, **kw):
        '''
        org detail view
        '''
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
            return [perm() for perm in self.read_permission_classes]
        if method == 'DELETE':
            IsOrgOwner = IsOrgOwnerOf(self.org)
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
        return Response([OrgSerializer(org).data for org in self.request.user.organizations])


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
        self.request.user.current_organization = validity_check(oid)
        self.request.user.save()
        return Response(status=204)


class OrgUserDetailAPIView(RetrieveUpdateAPIView):
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
