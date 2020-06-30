'''
校验权限
'''

from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)

from oneid_meta.models import (
    UserPerm,
    APP,
    User,
)
from oneid_meta.models.mixin import TreeNode as Node


class IsAdminUser(BasePermission):
    '''
    admin only
    '''
    def has_permission(self, request, view):
        '''
        admin only
        '''
        return request.user and request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, _):
        '''
        admin only
        '''
        return self.has_permission(request, view)


class IsManagerUser(BasePermission):
    '''
    manager only
    '''
    def has_permission(self, request, view):
        '''
        manager only
        '''
        return request.user and request.user.is_authenticated and request.user.is_manager

    def has_object_permission(self, request, view, _):
        '''
        manager only
        '''
        return self.has_permission(request, view)


class IsNotSettledinUser(IsAuthenticated):
    '''
    Allows access only to not settled users (password unset)
    '''
    def has_permission(self, request, view):
        return super().has_permission(request, view) and not request.user.is_settled


class IsNodeManager(BasePermission):
    """
    校验有无管理某节点的权限
    """
    def has_object_permission(self, request, view, obj):
        """
        对节点是否有管理权限
        """
        assert isinstance(obj, Node)
        return obj.under_manage(request.user)


class IsUserManager(BasePermission):
    '''
    校验有无管理某人的权限
    '''
    def has_object_permission(self, request, view, obj):
        '''
        对某人是否有管理权限
        '''
        assert isinstance(obj, User)
        return obj.under_manage(request.user)


class NodeEmployeeReadable(BasePermission):
    '''
    校验员工是否可见某节点
    '''
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Node)
        return obj.is_visible_to_employee(request.user)


class NodeManagerReadable(BasePermission):
    """
    校验管理员是否可见某节点
    包括：
    - 在管理范围内可见
    - 因下级节点可见而被迫可见
    """
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, Node)
        org = obj.org
        return org and request.user.is_org_manager(org) and obj.is_visible_to_manager(request.user)


class UserEmployeeReadable(BasePermission):
    '''
    校验员工是否可见某人
    '''
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, User)
        return obj.is_visible_to_employee(request.user)


class UserManagerReadable(BasePermission):
    '''
    校验管理员是否可见某人
    '''
    def has_object_permission(self, request, view, obj):
        assert isinstance(obj, User)
        return request.user.is_manager and obj.is_visible_to_manager(request.user)


class IsAPPManager(BasePermission):
    '''
    校验有无管理某应用的权限
    '''
    def has_object_permission(self, request, view, obj):
        assert obj.__class__ == APP
        return obj.under_manage(request.user)


class HasAPPAccess(BasePermission):
    '''
    校验有无进入某应用的权限
    也决定了能否看到该应用
    '''
    def has_object_permission(self, request, view, obj):
        assert obj.__class__ == APP
        app = obj
        user = request.user

        return UserPerm.valid_objects.filter(
            owner=user,
            perm__uid=f'app_{app.uid}_access',
            value=True,
        ).exists()


class IsManagerOf:
    '''
    是否为组织的管理员，默认检查当前组织
    '''
    def __new__(cls, *args):
        _cls = type('_IsManagerOf', (BasePermission, ), {'args': args})

        def has_permission(self, request, view):    # pylint: disable=unused-argument
            return request.user and request.user.is_authenticated and request.user.is_org_manager(*(self.args))

        def has_object_permission(self, request, view, _):
            return self.has_permission(request, view)

        setattr(_cls, 'has_permission', has_permission)
        setattr(_cls, 'has_object_permission', has_object_permission)

        return _cls


class IsOrgOwnerOf:
    '''
    是否为组织的拥有者，默认检查当前组织
    '''
    def __new__(cls, *args):
        _cls = type('_IsOrgOwnerOf', (BasePermission, ), {'args': args})

        def has_permission(self, request, view):    # pylint: disable=unused-argument
            '''
            org owner
            '''
            return request.user and request.user.is_authenticated and request.user.is_org_owner(*(self.args))

        def has_object_permission(self, request, view, _):
            '''
            org owner
            '''
            return self.has_permission(request, view)

        setattr(_cls, 'has_permission', has_permission)
        setattr(_cls, 'has_object_permission', has_object_permission)

        return _cls


class IsOrgMember:
    '''
    是否为组织的成员
    '''
    def __new__(cls, org):
        _cls = type('_IsOrgMember', (BasePermission, ), {'org': org})

        def has_permission(self, request, view):    # pylint: disable=unused-argument
            return request.user and request.user.is_authenticated and self.org in request.user.organizations

        def has_object_permission(self, request, view, _):
            return self.has_permission(request, view)

        setattr(_cls, 'has_permission', has_permission)
        setattr(_cls, 'has_object_permission', has_object_permission)

        return _cls


class CustomPerm():
    '''
    自定义权限，基于OneID自身Perm
    '''
    def __new__(cls, perm_uid):
        _cls = type('_CustomPerm', (BasePermission, ), {
            'perm_uid': perm_uid,
        })

        def has_permission(self, request, view):    # pylint: disable=unused-argument
            return UserPerm.valid_objects.filter(perm__uid=self.perm_uid, owner=request.user, value=True).exists()

        def has_object_permission(self, request, view, _):
            return self.has_permission(request, view)

        setattr(_cls, 'has_permission', has_permission)
        setattr(_cls, 'has_object_permission', has_object_permission)

        return _cls
