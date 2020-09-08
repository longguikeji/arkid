'''
刷新权限判定结果
'''
from datetime import datetime

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
    user_perms = UserPerm.valid_objects.all()
    group_perms = GroupPerm.valid_objects.all()
    dept_perms = DeptPerm.valid_objects.all()
    perms = Perm.valid_objects.all()
    users = User.valid_objects.all()
    groups = Group.valid_objects.all()
    depts = Dept.valid_objects.all()

    if user_perms.count() != perms.count() * users.count():
        for perm in perms:
            for user in users:
                if not user_perms.filter(Q(owner=user) | Q(perm=perm)).exists():
                    UserPerm.valid_objects.create(
                        owner=user,
                        perm=perm,
                        dept_perm_value=False,
                        group_perm_value=False,
                        status=0,
                        value=perm.default_value,
                    )

    if group_perms.count() != perms.count() * groups.count():
        for perm in perms:
            for group in groups:
                if not group_perms.filter(Q(owner=group) | Q(perm=perm)).exists():
                    GroupPerm.valid_objects.create(
                        owner=group,
                        perm=perm,
                        status=0,
                        value=perm.default_value,
                    )

    if dept_perms.count() != perms.count() * depts.count():
        for perm in perms:
            for dept in depts:
                if not dept_perms.filter(Q(owner=dept) | Q(perm=perm)).exists():
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

    time_a = datetime.now()
    check_app_default_perm()
    time_b = datetime.now()
    print(f'check_app_default_perm has done in {(time_b - time_a).seconds}s', )

    time_a = datetime.now()
    check_perm_exists()    # 现存瓶颈，待商榷
    time_b = datetime.now()
    print(f'check_perm_exists has done in {(time_b - time_a).seconds}s')

    time_a = datetime.now()
    flush_dept_perm(dept_perms=DeptPerm.valid_objects.all())
    time_b = datetime.now()
    print(f'flush_dept_perm has done in {(time_b - time_a).seconds}s')

    time_a = datetime.now()
    flush_group_perm(group_perms=GroupPerm.valid_objects.all())
    time_b = datetime.now()
    print(f'flush_group_perm has done in {(time_b - time_a).seconds}s')

    time_a = datetime.now()
    flush_user_perm()
    time_b = datetime.now()
    print(f'flush_user_perm has done in {(time_b - time_a).seconds}s')


def flush_group_perm(group=None, perms=None, group_perms=None):
    '''
    从上往下刷新组权限
    '''
    return _flush_node_perm(node_cls=Group, start_node=group, perms=perms, node_perms=group_perms, perm_cls=GroupPerm)


def flush_dept_perm(dept=None, perms=None, dept_perms=None):
    '''
    从上往下刷新部门权限
    '''
    return _flush_node_perm(node_cls=Dept, start_node=dept, perms=perms, node_perms=dept_perms, perm_cls=DeptPerm)


def _flush_node_perm(node_cls, start_node=None, perms=None, node_perms=None, perm_cls=None):
    '''
    从上往下刷新节点权限
    '''
    if not start_node:
        start_node = node_cls.get_root()
    if not perms:
        perms = Perm.valid_objects.all()
    if perm_cls and node_perms:
        if node_perms.count() != node_cls.valid_objects.all().count() * perms.count():
            for node in start_node.tree_front_walker():
                for perm in perms:
                    # TODO 批量创建
                    node_perm = node.get_perm(perm, node_perms)

                    # TODO 批量更新
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
    # pylint: disable=protected-access, no-member, invalid-name, line-too-long
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
                np.value = true and up.perm_id = np.perm_id
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
                np.value = true and up.perm_id = np.perm_id
        ''')
    else:
        for user in User.valid_objects.all():
            _update_user_node_perm(user)

    def update_value(x, boolean):
        x.value = boolean
        return x

    user_perms = []

    user_perms.extend([update_value(x, True) for x in UserPerm.valid_objects.filter(Q(status=1) & Q(value=False))])

    user_perms.extend([update_value(x, False) for x in UserPerm.valid_objects.filter(Q(status=-1) & Q(value=True))])

    user_perms.extend([
        update_value(x, True) for x in UserPerm.valid_objects.filter(
            Q(dept_perm_value=True) | Q(group_perm_value=True) & Q(status=0) & Q(value=False))
    ])

    user_perms.extend([
        update_value(x, False) for x in UserPerm.valid_objects.filter(
            Q(dept_perm_value=False) & Q(group_perm_value=False) & Q(status=0) & Q(value=True))
    ])

    UserPerm.objects.bulk_update(user_perms, fields=['value'])


if __name__ == '__main__':
    # pylint: disable=pointless-string-statement
    '''
    刷新所有权限
    '''
    flush_all_perm()
