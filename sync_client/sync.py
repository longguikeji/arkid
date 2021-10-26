from sync_client.utils import gen_user_attributes, gen_group_attributes
from sync_client.utils import gen_user_password, get_data
from sync_client.ldap_sync import SyncClientAD
from common.logger import logger
from config import get_app_config


def get_ldap_config():
    config = get_app_config()
    sync_client_config = config.data.get('sync_client')
    if not sync_client_config:
        return None
    return sync_client_config


def get_scim_data():
    users_url = 'http://localhost:80/scim/v2/Users'
    groups_url = 'http://localhost:80/scim/v2/Groups'
    users_data = get_data(users_url)
    groups_data = get_data(groups_url)
    users = [gen_user_attributes(user) for user in users_data['Resources']]
    groups = [gen_group_attributes(group) for group in groups_data['Resources']]
    # print(users)
    # print(groups)
    return users, groups


def sync():
    conf = get_ldap_config()
    if not conf or not conf.get('settings'):
        raise Exception("no sync_client config")
    settings = conf['settings']
    logger.info(f"sync_client: {settings}")
    if isinstance(settings, dict):
        settings = [settings]

    users, groups = get_scim_data()
    clients = []
    for conf in settings:
        client = SyncClientAD(**conf['domain_settings'])
        client.company = conf['company_name']
        client.company_id = conf['company_id']
        client.users = [user for user in users if user['company_name'] == conf['company_name']]
        client.groups = [group for group in groups if group['company_name'] == conf['company_name']]
        client.gen_user_password = gen_user_password
        clients.append(client)

    n = 1
    for client in clients:
        logger.info(f"syncing ad {n} with settings, {conf}")
        logger.info(f"users count: {len(client.users)}, groups count: {len(client.groups)}")
        client.user_search_clients = clients
        client.sync()
        n += 1

