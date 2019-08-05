'''
utils
- common-func for dept and group
'''

import re
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from pypinyin import lazy_pinyin as pinyin

from oneid_meta.models import Group, Dept, User
from executer.core import CLI
from executer.utils import operation


def data_masking(content, mask='******'):
    '''
    数据脱敏
    '''
    pattern = r'(?:(?<="password":")|(?<=secret":")|(?<=token":"))(.+?)(?=")'
    return re.sub(pattern, mask, content)


def gen_uid(name, cls=None, prefix='', suffix='', uid_field='uid'):
    '''
    生成uid
    :param str name: uid的关键部分，一般为中文名称
    :param cls cls: 如提供则提供唯一性检查并主动避免
    :param str prefix: 前缀
    :param str suffix: 后缀
    :param str uid_field: 唯一性检查时所用字段
    '''

    slug = ''.join(pinyin(name.lower()))
    slug = ''.join([item for item in slug if re.match(r'[a-z0-9]{1}', item)])
    pattern = '{prefix}{name}{digit}{suffix}'

    index = ''
    while True:
        uid = pattern.format(
            prefix=prefix,
            name=slug,
            digit=index,
            suffix=suffix,
        )
        if cls and cls.valid_objects.filter(**{uid_field: uid}).exists():
            if index:
                index += 1
            else:
                index = 1
        else:
            break

    return uid


def get_users_from_uids(user_uids):
    '''
    根据user uid按顺序返回user list
    :param list user_uids:
    '''
    try:
        users = User.get_from_pks(pks=user_uids, pk_name='username', raise_exception=True, is_del=False)
    except ObjectDoesNotExist as error:
        bad_uid = error.args[0]
        raise ValidationError({'user_uids': ['user:{} does not exist'.format(bad_uid)]})
    return users


def get_depts_from_uids(dept_uids):
    '''
    根据dept uid按顺序返回dept list
    '''
    try:
        depts = Dept.get_from_pks(pks=dept_uids, pk_name='uid', raise_exception=True, is_del=False)
    except ObjectDoesNotExist as error:
        bad_uid = error.args[0]
        raise ValidationError({'dept_uids': ['dept:{} does not exist'.format(bad_uid)]})
    return depts


def get_groups_from_uids(group_uids):
    '''
    根据group uid按顺序返回group list
    '''
    try:
        groups = Group.get_from_pks(pks=group_uids, pk_name='uid', raise_exception=True, is_del=False)
    except ObjectDoesNotExist as error:
        bad_uid = error.args[0]
        raise ValidationError({'group_uids': ['group:{} does not exist'.format(bad_uid)]})
    return groups


def update_users_of_owner(owner, users, subject):
    '''
    更新下属成员组成
    '''
    if isinstance(owner, Group):
        owner_type = 'group'
    if isinstance(owner, Dept):
        owner_type = 'dept'

    cli = CLI()
    add_func = getattr(cli, 'add_users_to_{}'.format(owner_type))
    delete_func = getattr(cli, 'delete_users_from_{}'.format(owner_type))
    sort_func = getattr(cli, 'sort_users_in_{}'.format(owner_type))

    if subject == 'add':
        add_func(users, owner)
    elif subject == 'delete':
        delete_func(users, owner)
    elif subject == 'sort':
        for user in users:
            check_func = getattr(user, 'if_belong_to_{}'.format(owner_type))
            if not check_func(owner, recursive=False):
                raise ValidationError({'user_uids': ['{} does not belong to this {}'.format(user, owner_type)]})
        sort_func(users, owner)
    elif subject == 'override':
        diff = operation.list_diff(users, owner.users)
        add_users = diff['>']
        delete_users = diff['<']
        add_func(add_users, owner)
        delete_func(delete_users, owner)
        sort_func(users, owner)
