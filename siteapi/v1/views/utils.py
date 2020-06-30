'''
utils
- common-func for dept and group
'''

import re
import uuid
import random
import string    # pylint: disable=deprecated-module
import base64
import json

from cryptography.fernet import Fernet, InvalidToken
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
from pypinyin import lazy_pinyin as pinyin

from oneid_meta.models import Group, Dept, User, AppGroup, APP
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
    if slug == '':
        slug = uuid.uuid4().hex[:10]
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


def get_apps_from_ids(app_ids):
    """
    根据app id按顺序返回app list
    :param list app_ids:
    """
    try:
        apps = APP.get_from_pks(pks=app_ids, pk_name='id', raise_exception=True, is_del=False)
    except ObjectDoesNotExist as error:
        bad_uid = error.args[0]
        raise ValidationError({'user_uids': ['app:{} does not exist'.format(bad_uid)]})
    return apps


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


def get_app_groups_from_uids(app_group_uids):
    """
    根据 app group uid 按顺序返回 app group list
    """
    try:
        app_groups = AppGroup.get_from_pks(pks=app_group_uids, pk_name='uid', raise_exception=True, is_del=False)
    except ObjectDoesNotExist as error:
        bad_uid = error.args[0]
        raise ValidationError({'app_group_uids': ['app_group:{} does not exist'.format(bad_uid)]})
    return app_groups


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


def update_apps_of_owner(owner, apps, subject):
    """
    更新下属应用成员组成
    """
    if isinstance(owner, AppGroup):
        owner_type = 'appgroup'

    cli = CLI()
    add_func = getattr(cli, 'add_apps_to_{}'.format(owner_type))
    delete_func = getattr(cli, 'delete_apps_from_{}'.format(owner_type))
    sort_func = getattr(cli, 'sort_apps_in_{}'.format(owner_type))

    if subject == 'add':
        add_func(apps, owner)
    elif subject == 'delete':
        delete_func(apps, owner)
    elif subject == 'sort':
        for app in apps:
            check_func = getattr(app, 'if_belong_to_{}'.format(owner_type))
            if not check_func(owner, recursive=False):
                raise ValidationError({'app_uids': ['{} does not belong to this {}'.format(app, owner_type)]})
        sort_func(apps, owner)
    elif subject == 'override':
        diff = operation.list_diff(apps, owner.apps)
        add_apps = diff['>']
        delete_apps = diff['<']
        add_func(add_apps, owner)
        delete_func(delete_apps, owner)
        sort_func(apps, owner)


class Secret():
    '''
    对提供的数据进行加加解密，并附带时间戳与随机数
    数据必须可以json序列化
    适用于简短字符串的加解密，其他场合不适合
    '''

    key = Fernet(base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32]))

    def __init__(self, **data):
        self.payload = {
            'timestamp': timezone.now().strftime('%Y%m%d%H%M%s'),
            'nonce': ''.join(random.choices(string.ascii_lowercase, k=16)),
            **data,
        }

    def __str__(self):
        # 去掉 `=` ，对 url 友好
        return self.key.encrypt(json.dumps(self.payload).encode()).decode('utf-8').replace('=', '')

    @classmethod
    def parse(cls, literal):
        '''
        load secret from literal
        '''

        # 补齐 `=`
        tail = '=' * (len(literal) % 4)
        literal += tail

        try:
            raw_payload = cls.key.decrypt(literal.encode())
        except InvalidToken:
            return None

        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            return None

        return cls(**payload)
