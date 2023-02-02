import json
import ldap3
from ldap3 import Server, Connection
from scim_server.schemas.core2_group import Core2Group
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.protocol.path import Path
from scim_server.utils import (
    compose_core2_user,
    compose_enterprise_extension,
    compose_core2_group,
    compose_core2_group_member,
)
from scim_server.schemas.member import Member
from arkid.common.logger import logger
from scim_server.schemas.user_groups import UserGroup as ScimUserGroup
import random
import string


def get_ad_connection(data):
    logger.info(f"Get AD Connection with config: {data}")
    host = data.get("host")
    port = data.get("port")
    use_tls = data.get("tls")
    bind_dn = data.get("bind_dn")
    bind_password = data.get("bind_password")
    server = Server(
        host=host,
        port=port,
        use_ssl=use_tls,
        get_info=ldap3.ALL,
        connect_timeout=data.get("connect_timeout"),
    )
    conn = Connection(
        server,
        user=bind_dn,
        password=bind_password,
        auto_bind=True,
        # raise_exceptions=False,
        receive_timeout=data.get("receive_timeout"),
        check_names=True,
    )
    return conn


def get_scim_group(value_dict, members, group_attr_map):
    group = Core2Group(displayName='')
    id_attr = None
    for ad_attr, scim_attr in group_attr_map.items():
        if scim_attr == 'id':
            id_attr = ad_attr
        value = value_dict.get(ad_attr)
        if isinstance(value, list):
            if value:
                value = value[0]
            else:
                value = None
        scim_path = Path.create(scim_attr)
        compose_core2_group(group, scim_path, value)

    for item in members:
        member = Member(value=item.get(id_attr))
        group.members.append(member)
    return group


def get_scim_user(value_dict, attr_map):
    scim_user = Core2EnterpriseUser(userName='', groups=[])
    for ad_attr, scim_attr in attr_map.items():
        value = value_dict.get(ad_attr)
        if isinstance(value, list):
            if value:
                value = value[0]
            else:
                value = None
        scim_path = Path.create(scim_attr)
        if (
            scim_path.schema_identifier
            and scim_path.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser
        ):
            compose_enterprise_extension(scim_user, scim_path, value)
        else:
            compose_core2_user(scim_user, scim_path, value)

    # 生成用户所在的组
    ouID = value_dict.get('ouID')
    if ouID:
        scim_user.groups.append(ScimUserGroup(value=ouID))
    return scim_user


def gen_user_attributes(user):
    data = {
        # 'cn': '',
        'givenName': user['name']['givenName'],
        'sn': user['name']['familyName'],
        'name': user['name']['formatted'].replace(',', ''),
        'displayName': user['name']['formatted'].replace(',', ''),
        'homePhone': str(
            user['emails'][0].get('value', '') if user.get('emails') else ''
        ),
        'userPrincipalName': user['userName'],
        'sAMAccountName': user['userName'],
        # 'userPassword': '', # generate_pwd_func and notify_by_api
        'employeeID': user['id'],
        # 'title': user.get('title', ''),
        # 'department': user['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User']
        # .get('department', '')
        # .strip('/'),
        # 'company': user['urn:ietf:params:scim:schemas:extension:hr:2.0:User']['FCOMP'],
        # 'manager': user['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User']['manager']['value'],
        # 'pager': str(
        #     user['phoneNumbers'][0].get('value', '') if user.get('phoneNumbers') else ''
        # ),
    }
    result = {}
    result['raw_data'] = user
    # result['id'] = user['userName']
    result['id'] = user['id']
    result['name'] = data['name']
    # result['mail'] = user.get('mail', '')
    # status = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User']['FSTATUS']
    # result['status'] = 'enabled' if str(status) == '1' else 'disabled'
    # result['group_id'] = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User'].get(
    #     'FDEPT_ID'
    # )
    # result['manager_id'] = (
    #     user['urn:ietf:params:scim:schemas:extension:enterprise:2.0:User']
    #     .get('manager', {})
    #     .get('value')
    # )
    result['attributes'] = data
    # while len(data['department']) > 64:
    #     data['department'] = data['department'].rsplit('/', 1)[0]
    # result['company_name'] = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User'][
    #     'FCOMP'
    # ]
    # result['company_id'] = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User'][
    #     'FCOMP_ID'
    # ]
    # result['join_date'] = user['urn:ietf:params:scim:schemas:extension:hr:2.0:User'][
    #     'FJOIN_DATE'
    # ].strip('/')
    return result


def gen_group_attributes(group):
    result = {}
    result['raw_data'] = group
    result['id'] = group['id']
    # status = group['urn:ietf:params:scim:schemas:extension:hr:2.0:Group']['FSTATUS']
    # result['status'] = 'enabled' if str(status) == '3' else 'disabled'
    result['name'] = group['displayName'].strip().strip('/').replace('/', '_')
    result['members'] = group.get('members', [])
    # result['manager_id'] = group[
    #     'urn:ietf:params:scim:schemas:extension:hr:2.0:Group'
    # ].get('FMANAGER')
    # result['company_name'] = group[
    #     'urn:ietf:params:scim:schemas:extension:hr:2.0:Group'
    # ]['FCOMP']
    # result['company_id'] = group['urn:ietf:params:scim:schemas:extension:hr:2.0:Group'][
    #     'FCOMP_ID'
    # ]
    return result


def gen_password(length):
    chars = [
        string.ascii_lowercase.replace('l', '').replace('o', ''),
        string.ascii_uppercase,
        string.digits,
        '@',
    ]
    passwd = []
    for i in range(0, 4):
        passwd.append(str(random.choice(chars[i])))
    for i in range(0, length - 4):
        passwd.append(str(random.choice(random.choice(chars))))
    random.shuffle(passwd)
    passwd = ''.join(passwd)
    return passwd
