"""
Override Dingding datasource to oneID
"""

import json
from thirdparty_data_sdk.dingding.dingsdk.department_manager import DepartmentManager
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.user_manager import UserManager
from oneid_meta.models.user import User, DingUser
from oneid_meta.models.group import Group, DingGroup
from oneid_meta.models.dept import Dept, DingDept
from oneid_meta.models import DingConfig
from oneid.settings import DINGDING_APP_VERSION

PAGE_DEFAULT_SIZE = 30
UNKNOWN_GENDER = 0
DEPARTMENT_ROOT_ID = '1'
DEPARTMENT_ROOT_UID = 'root'
GROUP_ROOT_UID = 'intra'
EXECUTERS = [    # 注意顺序
    'executer.RDB.RDBExecuter',
    # 'executer.LDAP.LDAPExecuter',
]

CREATE_DEPT_INFO = {'createDeptGroup': True, 'deptHiding': False, 'sourceIdentifier': 'source'}


def create_user_meta(user_manager, user):
    """
    创建user记录
    :param user:一条arkid_user数据
    :return:
    """
    user_info = {
        'name': user.name,
        'remark': user.remark,
        'mobile': user.mobile,
        'email': user.email,
        'active': user.is_active,
        'isAdmin': user.is_admin,
        'isBoss': user.is_boss,
        'isLeaderInDepts': user.is_manager,
        'department': [dept.ding_dept.uid for dept in user.ding_depts] +\
            [group.ding_group.uid for group in user.ding_groups],
        'position': user.position,
        'avatar': user.avatar,
        'jobnumber': user.employee_number,
        'private_email': user.private_email,
        'gender': user.gender,
        'account': user.mobile,
    }
    # 扫码登录用户可能存在ding_user,但是未记录钉钉uid,需要更新
    try:
        bind_ding_user = user.ding_user
        # 已绑定uid，更新用户信息
        try:
            uid = bind_ding_user.uid
            user_info.update({'userid': uid})
            user_manager.update_user(uid=uid, kwargs=user_info)
        # 未绑定uid，添加用户
        except Exception as err:    # pylint: disable=broad-except
            print('no ding_user uid==>', err)
            ret = user_manager.add_user(user.name, user.mobile, user_info['department'])
            if ret['errcode'] == '0':
                bind_ding_user.uid = ret['userid']
                bind_ding_user.account = user_info['mobile']
                bind_ding_user.save()
                user_manager.update_user(uid=ret['userid'], kwargs=user_info)

    # 未同步且未扫码绑定钉钉用户
    except Exception as err:    # pylint: disable=broad-except
        print('update ding_user error=>', err)

        # 添加并绑定钉钉用户
        try:
            ret = user_manager.add_user(user.name, user.mobile, user_info['department'])
            bind_ding_user = DingUser.objects.create(user=user, uid=ret['userid'],\
                account=user_info['mobile'], data=json.dumps({
                    'uname': user_info['name'],
                    'position': user_info['position'],
                    'remark': user_info['remark'],
                    'email': user_info['private_email'],
                    'orgemail': user_info['email'],
                    'jobnumber': user_info['jobnumber'],
                    'ishide': user_info['isHide'],
                }))

            # 更新并绑定openid, union_id
            ret = user_manager.get_user_detail(ret['userid'])
            if ret['errcode'] == 0:
                bind_ding_user.open_id = ret['openId']
                bind_ding_user.union_id = ret['unionid']
            bind_ding_user.save()
        except Exception as err:    # pylint: disable=broad-except
            print('add user error=>', err)


def create_node_meta(department_manager, node):
    """
    在钉钉上创建节点记录,已创建记录则更新
    :param node:一条arkid_node数据, 支持部门和角色
    :return:
    """
    for child in node.children:
        try:
            update_node_info = {
                'name': child.name,
                'parentid': node.ding_dept.uid if node.__class__.__name__ == 'Dept' else node.ding_group.uid,
                'order': child.order_no,
                'createDeptGroup': True,
                'autoAddUser': True,
                'deptHiding': child.visibility == 5,
                'sourceIdentifier': 'source',
            }
            ret = department_manager.update_dep(department_id=child.ding_dept.uid if node.__class__.__name__ == 'Dept'\
                else child.ding_group.uid, kwargs=update_node_info)
            if ret['errcode'] == 0:
                if isinstance(node, Dept):
                    new_ding_dept = DingDept.valid_objects.get(dept=child)
                    new_ding_dept.uid = ret['id']
                    new_ding_dept.save()
                elif isinstance(node, Group):
                    new_ding_group = DingGroup.valid_objects.get(group=child)
                    new_ding_group.uid = ret['id']
                    new_ding_group.save()

        except Exception as err:    # pylint: disable=broad-except
            print(err)
            try:
                if child.__class__.__name__ == 'Dept':
                    ret = department_manager.create_dep(node.ding_dept.uid, child.name)
                    bind_ding_node, _ = DingDept.objects.get_or_create(dept=child, uid=ret['id'])
                elif child.__class__.__name__ == 'Group':
                    ret = department_manager.create_dep(node.ding_group.uid, child.name)
                    bind_ding_node, _ = DingGroup.objects.get_or_create(group=child, uid=ret['id'])
                bind_ding_node.save()
            except Exception as err:    # pylint: disable=broad-except
                print(err)

        if child.children.exists():
            create_node_meta(department_manager, child)


def override_ding_dept(department_manager):
    '''
    push（部门）信息到钉钉
    '''
    # 绑定钉钉根部门组并创建子部门
    root_dept = Dept.valid_objects.filter(uid=DEPARTMENT_ROOT_UID).first()
    try:
        ret = department_manager.create_dep(1, '部门')
        if ret['errcode'] == 0:
            root_ding_dept = DingDept.valid_objects.create(dept=root_dept, uid=ret['id'])
            root_ding_dept.save()
    except Exception as err:    # pylint: disable=broad-except
        print('create error=>', err)
    create_node_meta(department_manager, root_dept)


def override_ding_role(department_manager):
    '''
    push节点（角色)信息到钉钉
    '''
    # 绑定钉钉根角色组并创建子角色
    root_group = Group.valid_objects.filter(uid='role').first()
    try:
        ret = department_manager.create_dep(DEPARTMENT_ROOT_ID, '角色')
        if ret['errcode'] == 0:
            root_ding_group = DingGroup.valid_objects.create(group=root_group, uid=ret['id'])
            root_ding_group.save()
    except Exception as err:    # pylint: disable=broad-except
        print('create error=>', err)
    create_node_meta(department_manager, root_group)


def override_ding_user(user_manager):
    '''
    push用户信息到钉钉
    '''
    users = User.valid_objects.exclude(is_boss=True).exclude(username='admin')
    for user in users:
        create_user_meta(user_manager, user)


def entrypoint():
    '''
    override dingding data
    '''
    ding_config = DingConfig.get_current()
    token_manager = AccessTokenManager(ding_config.app_key, ding_config.app_secret, DINGDING_APP_VERSION)
    department_manager = DepartmentManager(token_manager)
    user_manager = UserManager(token_manager)

    override_ding_dept(department_manager)
    override_ding_role(department_manager)
    override_ding_user(user_manager)


if __name__ == '__main__':
    entrypoint()
