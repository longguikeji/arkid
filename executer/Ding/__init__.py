"""
钉钉数据操作
"""
import json
import copy
from executer.core import Executer
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.constants import TOKEN_FROM_APPKEY_APPSECRET
from thirdparty_data_sdk.dingding.dingsdk.user_manager import UserManager
from thirdparty_data_sdk.dingding.dingsdk.department_manager import DepartmentManager
from thirdparty_data_sdk.dingding.dingsdk.role_manager import RoleManager
from oneid_meta.models import User, DeptMember, Dept, Group, DingConfig

DEFAULT_DEPT = '1'


class DingExecuter(Executer):
    """
    钉钉数据源操作类
    """
    def __init__(self, app_key=None, app_secret=None, app_version=None, agent_id=None):
        """
        初始化钉钉相关参数
        """
        if app_key and app_secret and app_version and agent_id:
            self.token_manager = AccessTokenManager(app_key, app_secret, app_version)
        else:
            ding_config = DingConfig.get_current()
            self.token_manager = AccessTokenManager(ding_config.app_key, ding_config.app_secret,
                                                    TOKEN_FROM_APPKEY_APPSECRET)

        self.user_manager = UserManager(self.token_manager)
        self.dept_manager = DepartmentManager(self.token_manager)
        self.role_manager = RoleManager(self.token_manager)

    def create_user(self, user_info):
        """
        创建用户
        """
        if 'ding_user' in user_info:
            data_dic = json.loads(user_info['ding_user']['data'])
            name = data_dic['name']
            del data_dic['name']
            res = self.user_manager.add_user(name, user_info['ding_user']['account'], DEFAULT_DEPT, **data_dic)
            user_item = User.valid_objects.filter(username=user_info['username']).first()
            if user_item and user_item.ding_user:
                user_item.ding_user.uid = res['userid']
                user_item.ding_user.save()
                return user_item.ding_user.uid

    def update_user(self, user, user_info):
        """
        更新用户
        """
        if 'ding_user' in user_info:
            if user.ding_user:
                data_dic = json.loads(user_info['ding_user']['data'])
                self.user_manager.update_user(user.ding_user.uid, **data_dic)

    def delete_users(self, users):
        """
        批量删除用户
        """
        for user in users:
            if user.ding_user:
                self.user_manager.delete_user(user.ding_user.uid)

    def create_dept(self, dept_info, org):
        """
        创建部门
        """
        if 'ding_dept' in dept_info:
            data_dic = json.loads(dept_info['ding_dept']['data'])
            res = self.dept_manager.create_dep(DEFAULT_DEPT, dept_info['name'], **data_dic)

            dept_item = Dept.valid_objects.filter(uid=dept_info['uid']).first()
            if dept_item.ding_dept:
                dept_item.ding_dept.uid = res['id']
                dept_item.ding_dept.save()
                return dept_item.ding_dept.uid

    def update_dept(self, dept, dept_info):
        """
        更新部门
        """
        if 'ding_dept' in dept_info:
            if dept.ding_dept:
                data_dic = json.loads(dept_info['ding_dept']['data'])
                self.dept_manager.update_dep(dept.ding_dept.uid, **data_dic)

    def delete_dept(self, dept):
        """
        删除部门
        """
        if dept.ding_dept:
            self.dept_manager.delete_dep(dept.ding_dept.uid)

    def add_dept_to_dept(self, dept, parent_dept):
        """
        将一个部门加入另一个部门作为后者子部门
        """
        if dept.ding_dept and parent_dept.ding_dept:
            self.dept_manager.update_dep(dept.ding_dept.uid, parentid=parent_dept.ding_dept.uid)

    def move_dept_to_dept(self, dept, parent_dept):
        """
        将一个部门移动到另一个部门下作为子部门
        """
        self.add_dept_to_dept(dept, parent_dept)

    def sort_depts_in_dept(self, depts, parent_dept):
        """
        调整子部门列表在父部门中的排序, 在父部门中的排序值，order值小的排序靠前
        """
        if parent_dept.ding_dept:
            orderids = []
            uids = []
            for dept in depts:
                if dept.ding_dept:
                    res = self.dept_manager.get_dep_detail(dept.ding_dept.uid)
                    orderids.append(res['order'])
                    uids.append(dept.ding_dept.uid)
            orderids.sort()
            for i, _ in enumerate(uids):
                self.dept_manager.update_dep(uids[i], order=orderids[i])

    def sort_users_in_dept(self, users, dept):
        """
        调整员工列表在部门中的排序, 列表是按order的倒序排列输出的，即从大到小排列输出的
        """
        if dept.ding_dept:
            orderids = []
            uids = []
            for user in users:
                if user.ding_user:
                    res = self.user_manager.get_user_detail(user.ding_user.uid)
                    dept_orders = json.loads(res['orderInDepts'])
                    orderids.append(dept_orders[dept.ding_dept.uid])
                    uids.append(user.ding_user.uid)
            orderids.sort(reverse=True)
            for i, _ in enumerate(uids):
                order_in_dept = '{%d:%d}' % (dept.ding_dept.uid, orderids[i])
                self.user_manager.update_user(uids[i], orderInDepts=order_in_dept)

    def add_user_to_depts(self, user, depts):
        """
        将一个用户加入一批部门
        :param oneid_meta.models.User user:
        :param list depts:
        :return:
        """
        user_already_in_depts = DeptMember.valid_objects.filter(user=user)
        for dept_item in user_already_in_depts:
            depts.append(dept_item.owner.ding_dept.uid)

        if user.ding_user:
            self.user_manager.update_user(user.ding_user.uid, department=depts)

    def delete_user_from_depts(self, user, depts):
        """
        将一个用户从一批部门中移除
        :param user:
        :param depts: list
        :return:
        """
        if user.ding_user:
            res = self.user_manager.get_user_detail(user.ding_user.uid)
            join_depts = res['department']
            for dept in depts:
                if dept.ding_dept:
                    join_depts.remove(dept.ding_dept.uid)
            self.user_manager.update_user(user.ding_user.uid, department=join_depts)

    def delete_users_from_dept(self, users, dept):
        """
        将一批人从部门中删除
        :param users: list
        :param dept:
        :return:
        """
        if dept.ding_dept:
            for user in users:
                if user.ding_user:
                    res = self.user_manager.get_user_detail(user.ding_user.uid)
                    join_depts = copy.deepcopy(res['department'])
                    join_depts.remove(dept.ding_dept.uid)
                    self.user_manager.update_user(user.ding_user.uid, department=join_depts)

    def add_users_to_dept(self, users, dept):
        """
        将一批用户加入一个部门
        :param list users:
        :param oneid_meta.models.Dept dept:
        """
        if dept.ding_dept:
            for user in users:
                depts = []
                user_already_in_depts = DeptMember.valid_objects.filter(user=user)
                if user.ding_user:
                    for dept_item in user_already_in_depts:
                        depts.append(dept_item.owner.uid)

                    ding_user_uid = user.ding_user.uid
                    depts.append(dept.ding_dept.uid)
                    self.user_manager.update_user(ding_user_uid, department=depts)

    def create_group(self, group_info, org):
        """
        创建组
        """
        if group_info['accept_user']:
            res = self.role_manager.create_role(group_info['name'], group_info['parent_uid'])
            group_item = Group.valid_objects.filter(uid=group_info['uid']).first()
            if group_item and group_item.ding_group:
                group_item.ding_group.uid = res['roleId']
                return group_item.ding_group.uid
        elif not group_info['accept_user']:
            res = self.role_manager.create_role_group(group_info['name'])
            group_item = Group.valid_objects.filter(uid=group_info['uid']).first()
            if group_item and group_item.ding_group:
                group_item.ding_group.uid = res['groupId']
                return group_item.ding_group.uid

    def update_group(self, group, group_info):
        """
        更新组
        """
        if group.ding_group:
            self.role_manager.update_role(group_info['name'], group.ding_group['uid'])

    def delete_group(self, group):
        """
        删除组
        """
        if group.ding_group:
            self.role_manager.delete_role(group.ding_group.uid)

    def create_app_group(self, app_group_info, org):
        """
        暂时无需与钉钉对接
        """

    def update_app_group(self, app_group, app_group_info):
        """
        暂时无需与钉钉对接
        """

    def delete_app_group(self, app_group):
        """
        暂时无需与钉钉对接
        """

    def add_users_to_group(self, users, group):
        """
        批量员工增加角色
        """
        if group.ding_group:
            user_ids = ''
            for user in users:
                if user.ding_user:
                    user_ids += user.ding_user.uid + ','

            self.role_manager.add_users_roles(str(group.ding_group.uid), user_ids[:-1])

    def add_user_to_groups(self, user, groups):
        """
        添加员工角色列表
        """
        if user.ding_user:
            group_ids = ''
            for group in groups:
                if group.ding_group:
                    group_ids += (str(group.ding_group.uid) + ',')

        self.role_manager.add_users_roles(group_ids[:-1], user.ding_user.uid)

    def delete_user_from_groups(self, user, groups):
        """
        删除员工角色列表
        """
        if user.ding_user:
            group_ids = ''
            for group in groups:
                if group.ding_group:
                    group_ids += (str(group.ding_group.uid) + ',')

            self.role_manager.delete_users_roles(group_ids[:-1], user.ding_user.uid)

    def delete_users_from_group(self, users, group):
        """
        批量删除员工角色
        """
        if group.ding_group:
            user_ids = ''
            for user in users:
                if user.ding_user:
                    user_ids += user.ding_user.uid + ','

            self.role_manager.delete_users_roles(str(group.ding_group.uid), user_ids[:-1])

    def add_group_to_group(self, group, parent_group):
        """
        创建组时已经做了加入
        """

    def move_group_to_group(self, group, parent_group):
        """
        钉钉需要角色下没有员工才可以删除
        """

    def sort_groups_in_group(self, groups, parent_group):
        """
        钉钉的角色没有顺序
        """

    def add_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        暂时无需与钉钉对接
        """

    def move_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        暂时无需与钉钉对接
        """

    def sort_appgroups_in_appgroup(self, app_groups, parent_app_group):
        """
        暂时无需与钉钉对接
        """

    def sort_users_in_group(self, users, group):
        """
        钉钉的角色没有顺序
        """

    def set_user_password(self, user, plaintext):
        """
        钉钉没有用户名密码
        """

    def add_apps_to_appgroup(self, apps, app_group):
        """
        将一批应用添加至一个应用分组
        Ding Ding中无需维护
        """

    def sort_apps_in_appgroup(self, apps, app_group):
        """
        调整一批应用在应用分组中的排序
        Ding Ding中无需维护
        """

    def delete_apps_from_appgroup(self, apps, app_group):
        """
        从应用分组中删除一批应用
        Ding Ding中无需维护
        """
