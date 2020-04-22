"""
Import Dingding datasource to oneID
"""

import json
from thirdparty_data_sdk.dingding.dingsdk.department_manager import DepartmentManager
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.user_manager import UserManager
from thirdparty_data_sdk.dingding.dingsdk.role_manager import RoleManager
from executer.core import cli_factory
from oneid_meta.models.user import User, DingUser
from oneid_meta.models.group import Group, GroupMember
from oneid_meta.models.dept import Dept, DeptMember, DingDept
from oneid_meta.models import DingConfig
from oneid.settings import DINGDING_APP_VERSION
from siteapi.v1.views.utils import gen_uid

PAGE_DEFAULT_SIZE = 30
UNKNOWN_GENDER = 0
DEPARTMENT_ROOT_ID = '1'
DEPARTMENT_ROOT_UID = 'root'
GROUP_ROOT_UID = 'intra'
EXECUTERS = [    # 注意顺序
    'executer.RDB.RDBExecuter',
    # 'executer.LDAP.LDAPExecuter',
]


def create_user_meta(db_executer, user):
    """
    创建user记录
    :param user:一条dinguser数据
    :return:
    """
    user_info = {
        'password': '',
        'name': user.get('name'),
        'private_email': user.get('email', ''),
        'email': user.get('orgEmail', ''),
        'mobile': user.get('mobile', ''),
        'employee_number': user.get('jobnumber', ''),
        'gender': UNKNOWN_GENDER,
        'ding_user': {
            'uid':
            user.get('userid'),
            'account':
            user.get('mobile', ''),
            'data':
            json.dumps({
                'uname': user.get('name'),
                'position': user.get('position', ''),
                'tel': user.get('tel', ''),
                'workplace': user.get('workPlace', ''),
                'remark': user.get('remark', ''),
                'email': user.get('email', ''),
                'orgemail': user.get('orgEmail', ''),
                'jobnumber': user.get('jobnumber', ''),
                'ishide': user.get('isHide', ''),
                'issenior': user.get('issenior', ''),
            })
        }
    }

    # 通过钉钉uid匹配
    exist_ding_user = DingUser.valid_objects.filter(uid=user.get('userid')).first()
    if exist_ding_user:
        return db_executer.update_user(exist_ding_user.user, user_info)

    # 通过手机号匹配
    exist_mobile_user = User.valid_objects.filter(mobile=user.get('mobile')).first()
    if exist_mobile_user:
        return db_executer.update_user(exist_mobile_user, user_info)

    # 通过私人邮箱匹配
    private_email = user.get('email', '')
    if private_email != '':
        exist_private_email_user = User.valid_objects.filter(private_email=private_email).first()
        if exist_private_email_user:
            return db_executer.update_user(exist_private_email_user, user_info)

    # 通过企业邮箱匹配
    email = user.get('orgEmail', '')
    if email != '':
        exist_email_user = User.valid_objects.filter(email=email).first()
        if exist_email_user:
            return db_executer.update_user(exist_email_user, user_info)

    user_info['username'] = gen_uid(user_info['name'], cls=User, uid_field='username')
    return db_executer.create_user(user_info)


def create_department_meta(db_executer, department):
    """
    创建department记录
    :param department: 一条dingdept数据
    :return:
    """
    dept_info = {
        'name': department.get('name'),
        'ding_dept': {
            'uid':
            department.get('id'),
            'data':
            json.dumps({
                'order': department.get('order', ''),
                'createDeptGroup': department.get('createDeptGroup', True),
                'deptHiding': department.get('deptHiding', False),
                'userpermit': department.get('userPermit', ''),
                'outerdep': department.get('outerDept', False),
                'outerpermitdepts': department.get('outerPermitDepts', ''),
                'outerpermitusers': department.get('outerPermitUsers', ''),
                'outerdeponlyself': department.get('outerDeptOnlySelf', False),
                'sourceIdentifier': department.get('sourceIdentifier', ''),
            })
        }
    }

    exist_ding_dept = DingDept.valid_objects.filter(uid=department.get('id')).first()
    if exist_ding_dept:
        return db_executer.update_dept(exist_ding_dept.dept, dept_info)
    dept_info['uid'] = gen_uid(dept_info['name'], cls=Dept)
    return db_executer.create_dept(dept_info)


def build_department_user_rawdata(db_executer, user_manager, department_manager, department_id, parent_dep):    # pylint: disable=too-many-locals
    """
    调用dingsdk生成供Dept，User，DeptMember使用的raw数据
    :param department_id: 部门id
    :param parent_dep: 父部门记录
    :return:
    """
    dep_detail = department_manager.get_dep_detail(department_id)
    dep_object = create_department_meta(db_executer, dep_detail)
    if dep_object.parent != parent_dep:
        db_executer.add_dept_to_dept(dep_object, parent_dep)
    index = 0
    is_continue = True
    tmp_user_list = []
    while is_continue:
        resp_users = department_manager.get_users_brief(department_id, size=PAGE_DEFAULT_SIZE, offset=index)
        is_continue = resp_users['hasMore']
        index += PAGE_DEFAULT_SIZE
        for user in resp_users['userlist']:
            user_detail = user_manager.get_user_detail(user['userid'])
            user_object = create_user_meta(db_executer, user_detail)
            if not DeptMember.valid_objects.get_queryset().filter(user=user_object, owner=dep_object).exists():
                tmp_user_list.append(user_object)

    db_executer.add_users_to_dept(tmp_user_list, dep_object)
    resp_deps = department_manager.get_subdep_list(str(department_id), False)
    for dep in resp_deps['department']:
        build_department_user_rawdata(db_executer, user_manager, department_manager, str(dep['id']), dep_object)


def build_user_group_rawdata(db_executer, role_manager, role_id, group_accept_user):
    """
    调用dingsdk生成供GroupMember使用的raw数据
    :param role_id: 角色id
    :param group_accept_user: 根Group记录
    :return:
    """
    index = 0
    is_continue = True
    user_obj_list = []
    while is_continue:
        role_user_list = role_manager.get_role_userlist(role_id, size=PAGE_DEFAULT_SIZE, offset=index)
        is_continue = role_user_list['result']['hasMore']
        index += PAGE_DEFAULT_SIZE

        for user in role_user_list['result']['list']:
            user_in_group = User.valid_objects.get_queryset().filter(ding_user__uid=user['userid']).first()
            if user_in_group and not GroupMember.valid_objects.filter(user=user_in_group,\
                owner=group_accept_user).exists():
                user_obj_list.append(user_in_group)

        db_executer.add_users_to_group(user_obj_list, group_accept_user)


def build_group_rawdata(db_executer, role_manager):
    """
    调用dingsdk生成供Group使用的raw数据
    """

    role_list_index = 0
    role_list_continue = True
    root_group = Group.valid_objects.get_queryset().get(uid=GROUP_ROOT_UID)
    while role_list_continue:
        role_list_detail = role_manager.get_roles_list(PAGE_DEFAULT_SIZE, role_list_index)
        role_list_continue = role_list_detail['result']['hasMore']
        role_list_index += PAGE_DEFAULT_SIZE
        for group in role_list_detail['result']['list']:
            group_info = {
                'name': group['name'],
                'parent': None,
                'accept_user': False,
                'ding_group': {
                    'uid': group['groupId'],
                    'subject': 'role',
                    'is_group': True,
                }
            }

            exist_group = Group.valid_objects.get_queryset().filter(ding_group__uid=group['groupId'],
                                                                    ding_group__subject='role',
                                                                    ding_group__is_group=True).first()
            if exist_group:
                group_without_user = db_executer.update_group(exist_group, group_info)
            else:
                group_info['uid'] = gen_uid(group_info['name'], cls=Group)
                group_without_user = db_executer.create_group(group_info)
                db_executer.add_group_to_group(group_without_user, root_group)

            for role in group['roles']:
                role_info = {
                    'name': role['name'],
                    'parent': group['groupId'],
                    'accept_user': True,
                    'ding_group': {
                        'uid': role['id'],
                        'subject': 'role',
                        'is_group': False,
                    }
                }

                exist_child_group = Group.valid_objects.get_queryset().filter(ding_group__uid=role['id'],
                                                                              ding_group__subject='role',
                                                                              ding_group__is_group=False).first()
                if exist_child_group:
                    group_accept_user = db_executer.update_group(exist_child_group, role_info)
                else:
                    role_info['uid'] = gen_uid(role_info['name'], cls=Group)
                    group_accept_user = db_executer.create_group(role_info)

                if group_accept_user.parent != group_without_user:
                    db_executer.add_group_to_group(group_accept_user, group_without_user)

                build_user_group_rawdata(db_executer, role_manager, role['id'], group_accept_user)


def entrypoint():
    '''
    import dingding data
    '''
    ding_config = DingConfig.get_current()
    token_manager = AccessTokenManager(ding_config.app_key, ding_config.app_secret, DINGDING_APP_VERSION)
    department_manager = DepartmentManager(token_manager)
    user_manager = UserManager(token_manager)
    role_manager = RoleManager(token_manager)
    db_executer = cli_factory(EXECUTERS)(User.objects.get(username='admin'))
    root_dep = Dept.objects.get(uid=DEPARTMENT_ROOT_UID)
    build_department_user_rawdata(db_executer, user_manager, department_manager, DEPARTMENT_ROOT_ID, root_dep)
    build_group_rawdata(db_executer, role_manager)


if __name__ == '__main__':
    entrypoint()
