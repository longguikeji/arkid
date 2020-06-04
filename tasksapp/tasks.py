'''
async tasks
'''

import celery
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from ldap3 import Server

from scripts import flush_perm, ldap_user_perm, ldap_aggregate_user, user_manager
from executer.LDAP.client import Connection
from infrastructure.utils.email import send_email as send_email_func
from oneid_meta.models import User, DingConfig
from oneid_meta.models.mixin import TreeNode as Node

logger = get_task_logger(__name__)    # pylint: disable=invalid-name


class BaseTask(celery.Task):    # pylint: disable=abstract-method
    '''
    base celery task
    '''
    def on_failure(self, exc, task_id, args, kwargs, info):    # pylint: disable=arguments-differ, unused-argument
        '''
        print err msg if failed
        '''
        import traceback    # pylint: disable=import-outside-toplevel
        logger.error(traceback.format_exc())


@shared_task
def demo():
    '''
    demo
    '''
    print('demo backend task')


@shared_task
def flush_user_perm_in_db():
    '''
    刷新数据库中用户的权限
    必须周期性执行
    '''
    flush_perm.flush_user_perm()


@shared_task
def update_user_perm_in_db(userid):
    '''
    刷新指定用户的所有权限。
    不包括
    '''
    user = User.valid_objects.filter(id=userid).first()
    if user:
        flush_perm.update_user_perm(user)


@shared_task
def flush_user_perm_in_ldap():
    '''
    刷新LDAP中用户的权限
    必须周期性执行
    '''
    conn = Connection(
        Server(settings.LDAP_SERVER),
        user=settings.LDAP_USER,
        password=settings.LDAP_PASSWORD,
        auto_bind=True,
        raise_exceptions=True,
    )
    ldap_user_perm.flush_user_perm(conn)


@shared_task
def aggregate_user_in_ldap_dept():
    '''
    从下往上聚合部门成员并逐节点保存
    '''
    conn = Connection(
        Server(settings.LDAP_SERVER),
        user=settings.LDAP_USER,
        password=settings.LDAP_PASSWORD,
        auto_bind=True,
        raise_exceptions=True,
    )
    ldap_aggregate_user.aggregate_user_in_dept(conn, settings.LDAP_DEPT_BASE)


@shared_task
def aggregate_user_in_ldap_group():
    '''
    从下往上聚合组成员并逐节点保存
    '''
    conn = Connection(
        Server(settings.LDAP_SERVER),
        user=settings.LDAP_USER,
        password=settings.LDAP_PASSWORD,
        auto_bind=True,
        raise_exceptions=True,
    )
    ldap_aggregate_user.aggregate_user_in_group(conn, settings.LDAP_GROUP_BASE)


@shared_task
def flush_all_perm_in_db():
    '''
    刷新数据库中部门、组、用户的权限
    不是必须
    '''
    flush_perm.flush_all_perm()


@shared_task(base=BaseTask)
def import_ding():
    '''
    导入钉钉数据
    '''
    from scripts.import_dingding_data import entrypoint as _import_ding    # pylint: disable=import-outside-toplevel
    _import_ding()


@shared_task(base=BaseTask)
def override_ding():
    '''
    覆盖钉钉数据
    '''
    from scripts.override_dingding_data import entrypoint as _override_ding    # pylint: disable=import-outside-toplevel
    _override_ding()


@shared_task(base=BaseTask)
def sync_ding():
    '''
    同步钉钉数据
    '''
    ding_config = DingConfig.get_current()
    if ding_config.sync_state == 'pull':
        import_ding()
    elif ding_config.sync_state == 'push':
        override_ding()
    elif ding_config.sync_state == '':
        return


@shared_task(base=BaseTask)
def rm_unbonded_user_task():
    '''
    删除不属于任何部门的用户
    '''
    user_manager.rm_unbonded_user()


@shared_task
def send_email(addrs, subject, content):
    '''
    发送邮件
    '''
    send_email_func(addrs, subject, content)


@shared_task
def update_nodes_cache(node_uids):
    '''
    更新节点缓存
    '''
    print("update_nodes_cache", node_uids)
    nodes = Node.retrieve_nodes(node_uids)
    for node in nodes:
        node.update_cache()


@shared_task
def update_users_cache(user_uids):
    '''
    更新用户缓存
    '''
    print('update_users_cache', user_uids)
    users = User.valid_objects.filter(username__in=user_uids)
    for user in users:
        user.update_cache()
