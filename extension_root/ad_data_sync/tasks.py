from celery import shared_task
from .utils_client import gen_user_attributes, gen_group_attributes, get_data
from .ldap_sync import SyncClientAD
from common.logger import logger


def get_scim_data(user_url, group_url):
    users_data = get_data(user_url)
    groups_data = get_data(group_url)
    users = [gen_user_attributes(user) for user in users_data['Resources']]
    groups = [gen_group_attributes(group) for group in groups_data['Resources']]
    # print(users)
    # print(groups)
    return users, groups


def sync_client(**kwargs):
    user_url = kwargs['user_url']
    group_url = kwargs['group_url']
    users, groups = get_scim_data(user_url, group_url)

    logger.info(f"syncing ad with settings: {kwargs}")
    logger.info(f"users count: {len(users)}, groups count: {len(groups)}")

    kwargs['users'] = users
    kwargs['groups'] = groups
    client = SyncClientAD(**kwargs)
    client.sync()


@shared_task(bind=True)
def sync(self, *args, **kwargs):
    try:
        sync_client(**kwargs)
    except Exception as exc:
        max_retries = kwargs.get('max_retries', 3)
        countdown = kwargs.get('retry_delay', 5*60)
        raise self.retry(exc=exc, max_retries=max_retries, countdown=countdown)
