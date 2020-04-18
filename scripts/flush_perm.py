'''
刷新权限判定结果
'''

from ..oneid_meta.models import User, Group, Dept
from ..oneid_meta.models import GroupPerm, DeptPerm, UserPerm, Perm
from ..oneid_meta.models import APP


def check_app_default_perm():
    '''
    确保每个APP的默认权限存在
    '''
    for app in APP.valid_objects.all():
        _ = app.default_perm


def check_perm_exists():
    '''
    为每个对象：user,gruop,dept创建perm判定结果
    '''
    for perm in Perm.valid_objects.all():
        for user in User.valid_objects.all():
            if not UserPerm.valid_objects.filter(owner=user, perm=perm).exists():
                UserPerm.valid_objects.create(
                    owner=user,
                    perm=perm,
                    dept_perm_value=False,
                    group_perm_value=False,
                    status=0,
                    value=perm.default_value,
                )
        for group in Group.valid_objects.all():
            if not GroupPerm.valid_objects.filter(owner=group, perm=perm).exists():
                GroupPerm.valid_objects.create(
                    owner=group,
                    perm=perm,
                    status=0,
                    value=perm.default_value,
                )
        for dept in Dept.valid_objects.all():
            if not DeptPerm.valid_objects.filter(owner=dept, perm=perm).exists():
                DeptPerm.valid_objects.create(
                    owner=dept,
                    perm=perm,
                    status=0,
                    value=perm.default_value,
                )


def flush_all_perm():
    '''
    刷新全部权限
    '''
    check_app_default_perm()
    check_perm_exists()
    flush_dept_perm()
    flush_group_perm()
    flush_user_perm()


def flush_group_perm(group=None, perms=None):
    '''
    从上往下刷新组权限
    '''
    return _flush_node_perm(node_cls=Group, start_node=group, perms=perms)


def flush_dept_perm(dept=None, perms=None):
    '''
    从上往下刷新部门权限
    '''
    return _flush_node_perm(node_cls=Dept, start_node=dept, perms=perms)


def _flush_node_perm(node_cls, start_node=None, perms=None):
    '''
    从上往下刷新节点权限
    '''
    if not start_node:
        start_node = node_cls.get_root()
    if not perms:
        perms = Perm.valid_objects.all()

    for node in start_node.tree_front_walker():
        for perm in perms:
            node_perm = node.get_perm(perm)
            node_perm.update_value()


def flush_user_perm(users=None, perms=None):
    '''
    刷新用户权限，需要周期性执行
    - user_perm.dept_perm_value
    - user_perm.group_perm_value
    - user_perm.value

    用户权限的判定结果依赖于group、dept的判定结果
    '''
    if not users:
        users = User.valid_objects.all()
    if not perms:
        perms = Perm.valid_objects.all()

    for user in users:
        for perm in perms:
            user_perm = user.get_perm(perm)
            user_perm.group_perm_value = GroupPerm.valid_objects.filter(owner__in=user.groups, perm=perm,
                                                                        value=True).exists()
            user_perm.dept_perm_value = DeptPerm.valid_objects.filter(owner__in=user.depts, perm=perm,
                                                                      value=True).exists()
            user_perm.update_value()


if __name__ == '__main__':
    # pylint: disable=pointless-string-statement
    '''
    刷新所有权限
    临时性脚本，不是必需
    '''
    flush_all_perm()
