'''
刷新权限判定结果
'''
from django.db.models import Q
from django.db import connection

from oneid_meta.models import User, Group, Dept
from oneid_meta.models import GroupPerm, DeptPerm, UserPerm, Perm, GroupMember, DeptMember, APP


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
    check_perm_exists()    # 现存瓶颈，待商榷
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


def _update_user_node_perm(user):
    '''
    刷新指定用户对所有权限的 group_perm_value, dept_perm_value
    '''
    dept_perm_ids = [item['perm_id'] for item in \
        DeptPerm.valid_objects.filter(owner__id__in=user.dept_ids, value=True).values('perm_id').distinct()
    ]
    UserPerm.valid_objects.filter(owner=user).update(dept_perm_value=False)
    UserPerm.valid_objects.filter(owner=user, perm__id__in=dept_perm_ids).update(dept_perm_value=True)

    group_perm_ids = [item['perm_id'] for item in \
        GroupPerm.valid_objects.filter(owner__id__in=user.group_ids, value=True).values('perm_id').distinct()
    ]
    UserPerm.valid_objects.filter(owner=user).update(group_perm_value=False)
    UserPerm.valid_objects.filter(owner=user, perm__id__in=group_perm_ids).update(group_perm_value=True)


def update_user_perm(user):
    '''
    刷新指定用户所有权限
    基于现有部门、组权限的分配结果进行计算，不包括部门、组权限的刷新
    '''
    _update_user_node_perm(user)
    UserPerm.valid_objects.filter(Q(dept_perm_value=True) | Q(group_perm_value=True), status=0,
                                  owner=user).update(value=True)
    UserPerm.valid_objects.filter(Q(dept_perm_value=False) & Q(group_perm_value=False), status=0,
                                  owner=user).update(value=False)


def flush_user_perm():
    # pylint: disable=protected-access, no-member
    '''
    刷新用户权限，需要周期性执行
    - user_perm.dept_perm_value
    - user_perm.group_perm_value
    - user_perm.value

    用户权限的判定结果依赖于group、dept的判定结果
    '''

    if connection.vendor == 'mysql':
        cursor = connection.cursor()

        cursor.execute(f'''
            UPDATE
                {UserPerm._meta.db_table} as up
            SET
                up.group_perm_value = false
        ''')

        cursor.execute(f'''
            UPDATE
                {UserPerm._meta.db_table} as up
                RIGHT JOIN {GroupMember._meta.db_table} as nm ON up.owner_id = nm.user_id
                LEFT JOIN {GroupPerm._meta.db_table} as np ON nm.owner_id = np.owner_id
            SET
                up.group_perm_value = true
            WHERE
                np.value = true
        ''')

        cursor.execute(f'''
            UPDATE
                {UserPerm._meta.db_table} as up
            SET
                up.dept_perm_value = false
        ''')

        cursor.execute(f'''
            UPDATE
                {UserPerm._meta.db_table} as up
                RIGHT JOIN {DeptMember._meta.db_table} as nm ON up.owner_id = nm.user_id
                LEFT JOIN {DeptPerm._meta.db_table} as np ON nm.owner_id = np.owner_id
            SET
                up.dept_perm_value = true
            WHERE
                np.value = true
        ''')
    else:
        for user in User.valid_objects.all():
            _update_user_node_perm(user)

    UserPerm.valid_objects.filter(status=1).update(value=True)
    UserPerm.valid_objects.filter(status=-1).update(value=False)
    UserPerm.valid_objects.filter(Q(dept_perm_value=True) | Q(group_perm_value=True), status=0).update(value=True)
    UserPerm.valid_objects.filter(Q(dept_perm_value=False) & Q(group_perm_value=False), status=0).update(value=False)


if __name__ == '__main__':
    # pylint: disable=pointless-string-statement
    '''
    刷新所有权限
    '''
    flush_all_perm()
