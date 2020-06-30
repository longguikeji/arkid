'''
数据操作日志写入RDB
'''
from django.urls import resolve

from executer.core import Executer, single_cli_factory
from oneid_meta.models import Log, RequestAccessLog, RequestDataClientLog

# TODO@saas: 1. add switch org log, 3. add system org change log
# pylint: disable=too-many-lines


class RDBLogExecuter(Executer):
    '''
    记录数据操作日志
    '''
    cli = None

    _access_log = None
    _data_log = None

    @property
    def access_log(self):
        '''
        请求记录日志
        '''
        if self.cli.request and not self._access_log:
            self._access_log = RequestAccessLog.parse(self.cli.request)
        return self._access_log

    @property
    def data_log(self):
        '''
        请求内容日志
        '''
        if self.cli.request and not self._data_log:
            self._data_log = RequestDataClientLog.parse(self.cli.request)
        return self._data_log

    def log(self, subject, summary, org=None):
        '''
        创建日志
        '''
        kwargs = {
            'user': self.cli.user,
            'subject': subject,
            'summary': summary,
            'access': self.access_log,
            'data': self.data_log
        }
        if org is not None:
            kwargs['org'] = org

        return Log.objects.create(**kwargs)    # pylint: disable=no-member

    def create_user(self, user_info):
        '''
        创建用户
        :param dict user_info:
        '''
        subject = 'user_create'
        summary = f'{self.cli.user.log_name} 创建新用户 {self.cli.res.log_name}'

        if self.cli.request:
            url_name = resolve(self.cli.request.path_info).url_name
            if url_name == 'user_register':
                subject = 'ucenter_register'
                summary = f'用户注册: {self.cli.user.log_name}'

        return self.log(subject, summary)

    def update_user(self, user, user_info):
        '''
        :param oneid_meta.models.User user:
        :param dict user_info:
        :rtype: oneid_meta.models.User
        '''
        subject = 'user_update'
        summary = f'{self.cli.user.log_name} 编辑用户({user.log_name})信息'

        if self.cli.request:
            url_name = resolve(self.cli.request.path_info).url_name
            if url_name == 'ucenter_profile':
                subject = 'ucenter_update'
                return None

        return self.log(subject, summary)

    def set_user_password(self, user, plaintext):
        '''
        设置密码
        :param oneid_meta.models.User user:
        :param str plaintext:
        '''
        subject = 'ucenter_reset_pwd'
        summary = f'{self.cli.user.log_name} 修改用户({user.log_name})密码'
        return self.log(subject, summary)

    def delete_users(self, users):
        '''
        :param list users:
        '''
        subject = 'user_delete'
        user_names = ','.join([user.log_name for user in users])
        summary = f'{self.cli.user.log_name}批量删除用户[{user_names}]'
        return self.log(subject, summary)

    def create_dept(self, dept_info, org):
        '''
        :param dict dept_info:
            + dept_id (number)
            + parent_uid (string) - 尽量不用
            + uid (string)
            + name (string)
            + remark (string)
            + ding_dept (object)
                + uid (string)
                + data (string) - json
        :rtype: oneid_meta.models.Dept
        '''

        subject = 'dept_create'
        summary = f"{self.cli.user.log_name}创建部门({dept_info['name']})"
        return self.log(subject, summary, org=org)

    def update_dept(self, dept, dept_info):
        '''
        :param oneid_meta.models.Dept dept:
        :param dict dept_info:
        :rtype: oneid_meta.models.Dept
        '''
        subject = 'dept_update'
        summary = f"{self.cli.user.log_name}编辑部门({dept.name})信息"
        return self.log(subject, summary, org=dept.org)

    def delete_dept(self, dept):
        '''
        :param oneid_meta.models.Dept
        '''
        subject = 'dept_delete'
        summary = f"{self.cli.user.log_name}删除部门({dept.name})"
        return self.log(subject, summary, org=dept.org)

    def create_group(self, group_info, org):
        '''
        :param dict group_info:
            + group_id (number)
            + parent_uid (string) - 尽量不用
            + uid (string)
            + name (string)
            + remark (string)
            + accept_user (boolean) - 是否接纳人员，对于角色组为否
        :rtype: oneid_meta.models.Group
        '''
        subject = 'group_create'
        summary = f"{self.cli.user.log_name}创建组({group_info['name']})"
        return self.log(subject, summary, org=org)

    def update_group(self, group, group_info):
        '''
        :param oneid_meta.models.Group group:
        :param dict group_info:
        :rtype: oneid_meta.models.Group
        '''
        subject = 'group_update'
        summary = f"{self.cli.user.log_name}编辑组({group.name})信息"
        return self.log(subject, summary, org=group.org)

    def delete_group(self, group):
        '''
        :param oneid_meta.models.Group group:
        '''
        subject = 'group_delete'
        summary = f"{self.cli.user.log_name}删除组({group.name})"
        return self.log(subject, summary, org=group.org)

    def create_app_group(self, app_group_info, org):
        """
        :param dict app_group_info:
            + app_group_id (number)
            + parent_uid (string) - 尽量不用
            + uid (string)
            + name (string)
            + remark (string)
        :rtype: oneid_meta.models.AppGroup
        """
        subject = 'app_group_create'
        summary = f"{self.cli.user.log_name}创建应用分组({app_group_info['name']})"
        return self.log(subject, summary, org=org)

    def update_app_group(self, app_group, app_group_info):
        """
        :param oneid_meta.models.AppGroup app_group:
        :param dict app_group_info:
        :rtype: oneid_meta.models.AppGroup
        """
        subject = 'app_group_update'
        summary = f"{self.cli.user.log_name}编辑应用分组({app_group.name})信息"
        return self.log(subject, summary, org=app_group.org)

    def delete_app_group(self, app_group):
        """
        :param oneid_meta.models.AppGroup app_group:
        """
        subject = 'app_group_delete'
        summary = f"{self.cli.user.log_name}删除应用分组({app_group.name})"
        return self.log(subject, summary, org=app_group.org)

    def add_users_to_dept(self, users, dept):
        '''
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''
        subject = 'dept_member'
        user_names = ','.join([user.log_name for user in users])
        summary = f"{self.cli.user.log_name}添加一批用户[{user_names}]至部门({dept.name})"
        return self.log(subject, summary, org=dept.org)

    def sort_users_in_dept(self, users, dept):
        '''
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''

        subject = 'dept_member'
        user_names = ','.join([user.log_name for user in users])
        summary = f"{self.cli.user.log_name}调整一批用户[{user_names}]在部门({dept.name})中的顺序"
        return self.log(subject, summary, org=dept.org)

    def add_user_to_depts(self, user, depts):
        '''
        :param oneid_meta.models.User user:
        :param list depts:
        '''
        subject = 'dept_member'
        node_names = ','.join([node.name for node in depts])
        summary = f"{self.cli.user.log_name}添加用户(f{user.log_name})至一批部门[{node_names}]"
        return self.log(subject, summary, org=depts[0].org if depts else None)

    def delete_users_from_dept(self, users, dept):
        '''
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''
        subject = 'dept_member'
        user_names = ','.join([user.log_name for user in users])
        summary = f"{self.cli.user.log_name}将一批用户[{user_names}]从部门({dept.name})删除"
        return self.log(subject, summary, org=dept.org)

    def delete_user_from_depts(self, user, depts):
        '''
        :param oneid_meta.models.User user:
        :param list depts:
        '''
        subject = 'dept_member'
        node_names = ','.join([node.name for node in depts])
        summary = f"{self.cli.user.log_name}将用户({user.log_name})从一批部门({node_names})删除"
        return self.log(subject, summary, org=depts[0].org if depts else None)

    def add_users_to_group(self, users, group):
        '''
        :param list users:
        :param oneid_meta.models.Group group:
        '''
        subject = 'group_member'
        user_names = ','.join([user.log_name for user in users])
        summary = f"{self.cli.user.log_name}添加一批用户[{user_names}]至组({group.name})"

        return self.log(subject, summary, org=group.org)

    def sort_users_in_group(self, users, group):
        '''
        :param list users:
        :param oneid_meta.models.Group group:
        '''
        subject = 'group_member'
        user_names = ','.join([user.log_name for user in users])
        summary = f"{self.cli.user.log_name}调整一批用户[{user_names}]在组({group.name})中的顺序"
        return self.log(subject, summary, org=group.org)

    def add_user_to_groups(self, user, groups):
        '''
        :param oneid_meta.models.User user:
        :param list groups:
        '''
        subject = 'group_member'
        node_names = ','.join([node.name for node in groups])
        summary = f"{self.cli.user.log_name}添加用户({user.log_name})至一批组({node_names})"
        return self.log(subject, summary, org=groups[0].org if groups else None)

    def delete_user_from_groups(self, user, groups):
        '''
        :param oneid_meta.models.User user:
        :param list groups:
        '''
        subject = 'group_member'
        node_names = ','.join([node.name for node in groups])
        summary = f"{self.cli.user.log_name}将用户({user.log_name})从一批组[{node_names}]删除"
        return self.log(subject, summary, org=groups[0].org if groups else None)

    def delete_users_from_group(self, users, group):
        '''
        :param list users:
        :param oneid_meta.models.Group group:
        '''
        subject = 'group_member'
        user_names = ','.join([user.log_name for user in users])
        summary = f"{self.cli.user.log_name}将一批用户[{user_names}]从组({group.name})删除"

        return self.log(subject, summary, org=group.org)

    def add_dept_to_dept(self, dept, parent_dept):
        '''
        将一个新部门加入到另一个部门作为其子部门
        :param oneid_meta.models.Dept dept:
        :param oneid_meta.models.Dept parent_dept:
        '''
        subject = 'dept_move'
        summary = f"{self.cli.user.log_name}将新部门({dept.name})加入到部门({parent_dept})下"
        return self.log(subject, summary, org=parent_dept.org)

    def move_dept_to_dept(self, dept, parent_dept):
        '''
        :param oneid_meta.models.Dept dept:
        :param oneid_meta.models.Dept parent_dept:
        '''
        subject = 'dept_move'
        summary = f"{self.cli.user.log_name}将部门({dept.name})移到部门({parent_dept.name})下"
        return self.log(subject, summary, org=parent_dept.org)

    def sort_depts_in_dept(self, depts, parent_dept):
        '''
        :param list depts:
        :param oneid_meta.models.Dept parent_dept:
        '''
        subject = 'dept_move'
        node_names = ','.join([node.name for node in depts])
        summary = f"{self.cli.user.log_name}调整部门({node_names})在部门({parent_dept.name})中的排序"
        return self.log(subject, summary, org=parent_dept.org)

    def add_group_to_group(self, group, parent_group):
        '''
        将一个新组加入到另一个组作为其子组
        :param oneid_meta.models.Group group:
        :param oneid_meta.models.Group parent_group:
        '''
        subject = 'group_move'
        summary = f"{self.cli.user.log_name}将新组({group.name})加入到组({parent_group.name})下"
        return self.log(subject, summary, org=parent_group.org)

    def move_group_to_group(self, group, parent_group):
        '''
        :param oneid_meta.models.Group group:
        :param oneid_meta.models.Group parent_group:
        '''
        subject = 'group_move'
        summary = f"{self.cli.user.log_name}将组({group.name})移到组({parent_group.name})下"
        return self.log(subject, summary, org=parent_group.org)

    def sort_groups_in_group(self, groups, parent_group):
        '''
        :param list groups:
        :param oneid_meta.models.Group parent_group:
        '''
        subject = 'group_sort'
        node_names = ','.join([node.name for node in groups])
        summary = f"{self.cli.user.log_name}调整组({node_names})在组({parent_group.name})中的排序"
        return self.log(subject, summary, org=parent_group.org)

    def add_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        将一个新应用分组加入到另一个应用分组作为其子应用分组
        :param oneid_meta.models.AppGroup app_group:
        :param oneid_meta.models.AppGroup parent_app_group:
        """
        subject = 'app_group_move'
        summary = f"{self.cli.user.log_name}将新应用分组({app_group.name})加入到应用分组({parent_app_group.name})下"
        return self.log(subject, summary, org=parent_app_group.org)

    def move_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        :param oneid_meta.models.AppGroup app_group:
        :param oneid_meta.models.AppGroup parent_app_group:
        """
        subject = 'app_group_move'
        summary = f"{self.cli.user.log_name}将应用分组({app_group.name})移到应用分组({parent_app_group.name})下"
        return self.log(subject, summary, org=parent_app_group.org)

    def sort_appgroups_in_appgroup(self, app_groups, parent_app_group):
        """
        :param list app_groups:
        :param oneid_meta.models.AppGroup parent_app_group:
        """
        subject = 'app_group_sort'
        node_names = ','.join([node.name for node in app_groups])
        summary = f"{self.cli.user.log_name}调整应用分组({node_names})在应用分组({parent_app_group.name})中的排序"
        return self.log(subject, summary, org=parent_app_group.org)

    # --- non-standard interface ---

    def create_app(self, app_info, org):
        '''
        创建应用
        '''
        subject = 'app_create'
        summary = f"{self.cli.user.log_name}创建应用({app_info['name']})"
        return self.log(subject, summary, org)

    def update_app(self, app, app_info):    # pylint: disable=unused-argument
        '''
        更新应用
        '''
        subject = 'app_update'
        summary = f"{self.cli.user.log_name}更新应用({app.name})"
        return self.log(subject, summary, app.owner)

    def delete_app(self, app):
        '''
        删除应用
        '''
        subject = 'app_delete'
        summary = f"{self.cli.user.log_name}删除应用({app.name})"
        return self.log(subject, summary, app.owner)

    def create_perm(self, perm):
        '''
        创建权限
        '''
        subject = 'perm_create'
        summary = f"{self.cli.user.log_name}创建权限({perm.name}({perm.uid}))"
        return self.log(subject, summary)

    def delete_perm(self, perm):
        '''
        删除权限
        '''
        subject = 'perm_delete'
        summary = f"{self.cli.user.log_name}删除权限({perm.name}({perm.uid}))"
        return self.log(subject, summary)

    def assign_user_perms(self, user):
        '''
        向用户分配权限
        '''
        subject = 'perm_assign'
        summary = f"{self.cli.user.log_name}修改用户({user.log_name})权限"
        return self.log(subject, summary)

    def assign_node_perms(self, node):
        '''
        向节点分配权限
        '''
        subject = 'perm_assign'
        summary = f"{self.cli.user.log_name}修改节点({node.name})权限"
        return self.log(subject, summary)

    def assign_perm_owners(self, perm):
        '''
        修改权限黑白名单
        '''
        subject = 'perm_assign'
        summary = f'{self.cli.user.log_name}修改权限({perm.name}({perm.uid}))的黑白名单'
        return self.log(subject, summary)

    def user_login(self):
        '''
        用户登录
        '''
        subject = 'ucenter_login'
        summary = f'{self.cli.user.log_name}登录'
        return self.log(subject, summary)

    def user_reset_password(self):
        '''
        用户重置密码
        '''
        subject = 'ucenter_reset_pwd'
        summary = f'{self.cli.user.log_name}重置密码'
        return self.log(subject, summary)

    def user_register(self):
        '''
        新用户注册
        '''
        subject = 'ucenter_register'
        summary = f'{self.cli.user.log_name}注册成功'
        return self.log(subject, summary)

    def user_activate(self):
        '''
        激活用户
        '''
        subject = 'ucenter_activate'
        summary = f'{self.cli.user.log_name}激活成功'
        return self.log(subject, summary)

    def update_config(self):
        '''
        更新系统配置
        '''
        subject = 'config'
        summary = f'{self.cli.user.log_name}更新系统配置'
        return self.log(subject, summary)

    def update_org_config(self, org):
        '''
        更新组织配置
        '''
        subject = 'org_config'
        summary = f'{self.cli.user.log_name}更新组织配置'
        return self.log(subject, summary, org)

    def add_apps_to_appgroup(self, apps, app_group):
        """
        将一批应用添加至一个应用分组
        :param list apps:
        :param oneid_meta.models.AppGroup app_group:
        """
        subject = 'app_group_member'
        app_names = ','.join([app.name for app in apps])
        summary = f"{self.cli.user.log_name}添加一批应用[{app_names}]至组({app_group.name})"
        return self.log(subject, summary, org=app_group.org)

    def sort_apps_in_appgroup(self, apps, app_group):
        """
        :param list apps:
        :param oneid_meta.models.AppGroup app_group:
        """
        subject = 'app_group_member'
        app_names = ','.join([app.name for app in apps])
        summary = f"{self.cli.user.log_name}调整一批应用[{app_names}]在组({app_group.name})中的顺序"
        return self.log(subject, summary, org=app_group.org)

    def delete_apps_from_appgroup(self, apps, app_group):
        """
        :param list apps:
        :param oneid_meta.models.AppGroup app_group:
        """
        subject = 'app_group_member'
        app_names = ','.join([app.name for app in apps])
        summary = f"{self.cli.user.log_name}将一批应用[{app_names}]从组({app_group.name})删除"
        return self.log(subject, summary, org=app_group.org)


LOG_CLI = single_cli_factory('executer.log.rdb.RDBLogExecuter')    # pylint: disable=invalid-name
