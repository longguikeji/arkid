'''
数据操作
'''

from django.utils.module_loading import import_string
from django.conf import settings

from common.django.middleware import CrequestMiddleware


class Executer():
    '''
    各模块的操作数据
    '''
    def create_user(self, user_info):
        '''
        :param dict data:
            + username (string)
            + name (string)
            + email (string)
            + mobile (string)
            + last_login (string) - format "2017-09-25 14:07"
            + number (string) - 工号
            + gender (enum[number])
                + 1 - 男
                + 2 - 女
            + ding_user (object) - May Null-> {}
                + user_id (string)
                + mobile (string)
            + posix_user (object) - May Null-> {}
                + uid
                + gid
                + home
                + pub_key
        :rtype: oneid_meta.models.User
        '''
        raise NotImplementedError

    def update_user(self, user, user_info):
        '''
        :param oneid_meta.models.User user:
        :param dict user_info:
        :rtype: oneid_meta.models.User
        '''
        raise NotImplementedError

    def set_user_password(self, user, plaintext):
        '''
        设置密码
        :param oneid_meta.models.User user:
        :param str plaintext:
        '''
        raise NotImplementedError

    def delete_users(self, users):
        '''
        :param list users:
        '''
        raise NotImplementedError

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
        raise NotImplementedError

    def update_dept(self, dept, dept_info):
        '''
        :param oneid_meta.models.Dept dept:
        :param dict dept_info:
        :rtype: oneid_meta.models.Dept
        '''
        raise NotImplementedError

    def delete_dept(self, dept):
        '''
        :param oneid_meta.models.Dept
        '''
        raise NotImplementedError

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
        raise NotImplementedError

    def update_group(self, group, group_info):
        '''
        :param oneid_meta.models.Group group:
        :param dict group_info:
        :rtype: oneid_meta.models.Group
        '''
        raise NotImplementedError

    def delete_group(self, group):
        '''
        :param oneid_meta.models.Group group:
        '''
        raise NotImplementedError

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
        raise NotImplementedError

    def update_app_group(self, app_group, app_group_info):
        """
        :param oneid_meta.models.AppGroup app_group:
        :param dict app_group_info:
        :rtype: oneid_meta.models.AppGroup
        """
        raise NotImplementedError

    def delete_app_group(self, app_group):
        """
        :param oneid_meta.models.AppGroup app_group:
        """
        raise NotImplementedError

    def add_users_to_dept(self, users, dept):
        '''
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''
        raise NotImplementedError

    def sort_users_in_dept(self, users, dept):
        '''
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''
        raise NotImplementedError

    def add_user_to_depts(self, user, depts):
        '''
        :param oneid_meta.models.User user:
        :param list depts:
        '''
        raise NotImplementedError

    def delete_users_from_dept(self, users, dept):
        '''
        :param list users:
        :param oneid_meta.models.Dept dept:
        '''
        raise NotImplementedError

    def delete_user_from_depts(self, user, depts):
        '''
        :param oneid_meta.models.User user:
        :param list depts:
        '''
        raise NotImplementedError

    def add_users_to_group(self, users, group):
        '''
        :param list users:
        :param oneid_meta.models.Group group:
        '''
        raise NotImplementedError

    def sort_users_in_group(self, users, group):
        '''
        :param list users:
        :param oneid_meta.models.Group group:
        '''
        raise NotImplementedError

    def add_user_to_groups(self, user, groups):
        '''
        :param oneid_meta.models.User user:
        :param list groups:
        '''
        raise NotImplementedError

    def delete_user_from_groups(self, user, groups):
        '''
        :param oneid_meta.models.User user:
        :param list groups:
        '''
        raise NotImplementedError

    def delete_users_from_group(self, users, group):
        '''
        :param list users:
        :param oneid_meta.models.Group group:
        '''
        raise NotImplementedError

    def add_dept_to_dept(self, dept, parent_dept):
        '''
        将一个新部门加入到另一个部门作为其子部门
        :param oneid_meta.models.Dept dept:
        :param oneid_meta.models.Dept parent_dept:
        '''
        raise NotImplementedError

    def move_dept_to_dept(self, dept, parent_dept):
        '''
        :param oneid_meta.models.Dept dept:
        :param oneid_meta.models.Dept parent_dept:
        '''
        raise NotImplementedError

    def sort_depts_in_dept(self, depts, parent_dept):
        '''
        :param list depts:
        :param oneid_meta.models.Dept parent_dept:
        '''
        raise NotImplementedError

    def add_group_to_group(self, group, parent_group):
        '''
        将一个新组加入到另一个组作为其子组
        :param oneid_meta.models.Group group:
        :param oneid_meta.models.Group parent_group:
        '''
        raise NotImplementedError

    def move_group_to_group(self, group, parent_group):
        '''
        :param oneid_meta.models.Group group:
        :param oneid_meta.models.Group parent_group:
        '''
        raise NotImplementedError

    def sort_groups_in_group(self, groups, parent_group):
        '''
        :param list groups:
        :param oneid_meta.models.Group parent_group:
        '''
        raise NotImplementedError

    def add_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        将一个新应用分组加入到另一个应用分组作为其子应用分组
        :param oneid_meta.models.AppGroup app_group:
        :param oneid_meta.models.AppGroup parent_app_group:
        """
        raise NotImplementedError

    def move_appgroup_to_appgroup(self, app_group, parent_app_group):
        """
        :param oneid_meta.models.AppGroup app_group:
        :param oneid_meta.models.AppGroup parent_app_group:
        """
        raise NotImplementedError

    def sort_appgroups_in_appgroup(self, app_groups, parent_app_group):
        """
        :param list app_groups:
        :param oneid_meta.models.AppGroup parent_app_group:
        """
        raise NotImplementedError

    def add_apps_to_appgroup(self, apps, app_group):
        """
        :param list apps:
        :param oneid_meta.models.AppGroup app_group:
        """
        raise NotImplementedError

    def delete_apps_from_appgroup(self, apps, app_group):
        """
        :param list apps:
        :param oneid_meta.models.AppGroup app_group:
        """
        raise NotImplementedError

    def sort_apps_in_appgroup(self, apps, app_group):
        """
        :param list apps:
        :param oneid_meta.models.AppGroup app_group:
        """
        raise NotImplementedError


FUNC_NAMES = [
    'create_user',
    'update_user',
    'set_user_password',
    'delete_users',
    'create_dept',
    'update_dept',
    'delete_dept',
    'create_group',
    'update_group',
    'delete_group',
    'create_app_group',
    'update_app_group',
    'delete_app_group',
    'add_users_to_dept',
    'sort_users_in_dept',
    'add_user_to_depts',
    'delete_users_from_dept',
    'delete_user_from_depts',
    'add_users_to_group',
    'sort_users_in_group',
    'add_user_to_groups',
    'delete_user_from_groups',
    'delete_users_from_group',
    'add_dept_to_dept',
    'move_dept_to_dept',
    'sort_depts_in_dept',
    'add_group_to_group',
    'move_group_to_group',
    'sort_groups_in_group',
    'add_appgroup_to_appgroup',
    'move_appgroup_to_appgroup',
    'sort_appgroups_in_appgroup',
    'add_apps_to_appgroup',
    'delete_apps_from_appgroup',
    'sort_apps_in_appgroup',
]

# 注册时，只有操作完成后才知道操作者身份
IDENTIFIED_DELAY_FUNC_NAMES = {
    'create_user': lambda user: {
        'user': user
    },
}


class CLIException(Exception):
    '''
    base exception of CLI
    '''


class ExecuteCLI(Executer):    # pylint: disable=abstract-method
    '''
    操作数据(跨模块)
    '''

    user = None
    request = None

    def __init__(self, user=None):
        self.identify(user, raise_exception=False)

    def identify(self, user=None, raise_exception=True):
        '''
        录入操作者身份及操作背景
        参数中的user优先级最高，其次是self.user，request.user最低
        cli.user，cli.request只允许从None修改为非None，最后不允许修改
        最终user必须有效
        '''
        request = CrequestMiddleware.get_request()

        if user:
            if getattr(self.user, 'is_authenticated', False):
                if user != self.user:
                    raise CLIException("can't reuse cli across different users")
            else:
                self.user = user

        if self.request:
            if self.request != request:
                raise CLIException("can't reuse cli across different requests")
        else:
            self.request = request

        if (not self.user) and self.request:
            user = getattr(self.request, 'user', None)
            if user and getattr(user, 'is_authenticated', False):
                self.user = user

        if not raise_exception:
            return

        if not self.user or not getattr(self.user, 'is_authenticated', False):
            raise CLIException("authenticated user is required")


def cli_factory(executer_clses):
    '''
    gen CLI class
    '''
    CLI_CLASS = type(
        'CLI',
        (ExecuteCLI, ),
        {
            'executers': [],
            'executer_clses': [],
            'access_log': None,
            'data_log': None,
        },
    )

    # executer_clses
    for executer_cls in executer_clses:
        if isinstance(executer_cls, str):
            cls = import_string(executer_cls)
        elif issubclass(executer_cls, Executer):
            cls = executer_cls
        else:
            raise CLIException(f"invalid executer cls:{executer_cls}")
        CLI_CLASS.executer_clses.append(cls)

    # __init__
    def __init__(self, *args, **kwargs):
        super(CLI_CLASS, self).__init__(*args, **kwargs)
        self.executers = []
        for executer_cls in self.executer_clses:
            executer = executer_cls()
            executer.cli = self
            self.executers.append(executer)

    CLI_CLASS.__init__ = __init__

    # funcs
    for func_name in FUNC_NAMES:

        def func(self, *args, fcn=func_name, **kwargs):
            if fcn not in IDENTIFIED_DELAY_FUNC_NAMES:
                self.identify()
            res = None
            for executer in self.executers:
                try:
                    executer_res = getattr(executer, fcn)(*args, **kwargs)
                    if executer.__class__.__name__ == 'RDBExecuter':
                        # 以RDBExecuter返回结果为准。各模块异常情况以报错形式抛出
                        res = executer_res
                        self.res = res
                        if fcn in IDENTIFIED_DELAY_FUNC_NAMES:
                            if not self.user:
                                self.identify(**IDENTIFIED_DELAY_FUNC_NAMES[fcn](res))
                except NotImplementedError:
                    if not settings.EXECUTER_WIP:
                        raise    # TODO: rm this
            return res

        setattr(CLI_CLASS, func_name, func)
    return CLI_CLASS


def single_cli_factory(executer_cls):
    '''
    gen CLI class with single executer
    可运行executer内的非标准接口
    '''
    class CLI_CLASS(cli_factory([executer_cls])):    # pylint: disable=abstract-method, invalid-name, missing-class-docstring
        def __getattribute__(self, name):
            try:
                return super().__getattribute__(name)
            except AttributeError:
                return self.executers[0].__getattribute__(name)

    return CLI_CLASS


CLI = cli_factory(settings.EXECUTERS)
