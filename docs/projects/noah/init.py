'''
Noah 初始化脚本
'''

from ....oneid_meta.models import Group, User

from ....executer.core import cli_factory


def entrypoint():
    '''
    main
    '''
    init_group()


def init_group():
    '''
    创建必要的组
    '''
    root = Group.valid_objects.get(uid='root')
    cli = cli_factory([
        'executer.RDB.RDBExecuter',
        'executer.LDAP.LDAPExecuter',
    ])(User.objects.first())
    intra = cli.create_group({'uid': 'intra', 'name': '内部联系人-角色'})
    extern = cli.create_group({'uid': 'extern', 'name': '外部联系人-标签'})
    managers = cli.create_group({'uid': 'manager', 'name': '管理员'})
    cli.add_group_to_group(intra, root)
    cli.add_group_to_group(extern, root)
    cli.add_group_to_group(managers, root)


if __name__ == '__main__':
    entrypoint()
