import re
import copy
import json
import datetime
import ldap3
from ldap3 import Server, Connection
from ldap3.extend.microsoft.addMembersToGroups import ad_add_members_to_groups
from ldap3.extend.microsoft.removeMembersFromGroups import ad_remove_members_from_groups
from scim_server.protocol.path import Path
from arkid.common.logger import logger
from .utils import (
    gen_password,
)
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.utils import scim_obj_to_client_obj
from ldap3 import Tls


class ADSyncClient:
    user_object_class = "user"
    # group_object_class = "group"
    ou_object_class = "organizationalUnit"

    def __init__(self, config, sync_log, groups, users):
        self.config = config
        self.sync_log = sync_log
        self.host = config["host"]
        self.port = config["port"]
        self.use_tls = config["use_tls"]
        self.bind_dn = config["bind_dn"]
        self.bind_password = config["bind_password"]
        self.root_dn = config["root_dn"]
        self.connect_timeout = config.get("connect_timeout")
        self.receive_timeout = config.get("receive_timeout")

        self.user_attr_map = config.get('user_attr_map', [])
        # self.group_attr_map = json.loads(config.get('group_attr_map'))
        self.match_attr = self.get_match_attr(self.user_attr_map)

        self.users = [
            self.gen_user_attributes(user, self.user_attr_map) for user in users
        ]
        self.groups = [self.gen_group_attributes(group) for group in groups]
        self.ldap_server_type = config.get("ldap_server_type")
        if self.ldap_server_type == 'AD':
            self.user_object_class = "user"
            self.ou_object_class = "organizationalUnit"
        elif self.ldap_server_type == 'openldap':
            self.user_object_class = "inetOrgPerson"
            self.ou_object_class = "organizationalUnit"

        self.conn = self.get_connection()

    def get_match_attr(self, attr_map):
        for item in attr_map:
            if item.get('is_match_attr'):
                return item.get('target_attr')

    def gen_user_attributes(self, scim_user, attr_map):
        result = {}

        attr_map = [(m.get("source_attr"), m.get("target_attr")) for m in attr_map]
        data = scim_obj_to_client_obj(scim_user, attr_map)
        result['attributes'] = data
        result['raw_data'] = scim_user
        result['id'] = data.get(self.match_attr)
        result['cn'] = scim_user['userName']
        active = scim_user.get('active')
        if active is None:
            result['active'] = True
        else:
            result['active'] = active
        groups = scim_user.get('groups', [])
        if groups:
            result['group_id'] = scim_user.get('groups')[0].get("value")
        else:
            result['group_id'] = None
        return result

    def gen_group_attributes(self, scim_group):
        result = {}
        result['raw_data'] = scim_group
        result['id'] = scim_group['id']
        result['name'] = scim_group['displayName'].strip()
        result['members'] = scim_group.get('members', [])
        return result

    def get_connection(self):
        # import ssl
        # tls = Tls(validate=ssl.CERT_REQUIRED, version=ssl.PROTOCOL_TLSv1_2)
        server = Server(
            host=self.host,
            port=self.port,
            use_ssl=self.use_tls,
            get_info=ldap3.ALL,
            # tls=tls,
            connect_timeout=self.connect_timeout,
        )

        conn = Connection(
            server,
            user=self.bind_dn,
            password=self.bind_password,
            auto_bind=True,
            # raise_exceptions=False,
            receive_timeout=self.receive_timeout,
        )
        return conn

    def add_user(self, user: json):
        object_class = self.user_object_class
        attributes = copy.copy(user["attributes"])
        dn = user["ldap_dn"]

        attributes = {k: v for k, v in attributes.items() if v}

        # add user
        res = self.conn.add(dn=dn, object_class=object_class, attributes=attributes)
        logger.info(
            f"=== Add user {res and 'success' or 'failed'}===: dn: {dn}, object_class: {object_class}, attributes: {attributes}, error: {res and 'None' or self.conn.result}"
        )
        self.sync_log.users_created += 1
        # set initial password
        # user_password = gen_password(8)
        # logger.debug(
        #     f"password: {user_password} generated for user: {user['cn']} id: {user['id']}"
        # )
        # self.set_user_password(dn, user_password)
        # if user['active']:
        #     self.enable_user(dn)

        if self.ldap_server_type == 'AD':
            self.enable_user(dn)

    def set_user_password(self, user_dn: str, user_password: str):
        # set password
        res = self.conn.extend.microsoft.modify_password(
            user_dn, new_password=user_password, old_password=None
        )
        logger.info(
            f"=== Setting user password {res and 'success' or 'failed'}===: dn: {user_dn}, error: {res and 'None' or self.conn.result}"
        )
        # User must change password at next logon
        password_expire = {"pwdLastSet": [(ldap3.MODIFY_REPLACE, [0])]}
        res = self.conn.modify(dn=user_dn, changes=password_expire)
        logger.info(
            f"=== Setting user password expire {res and 'success' or 'failed'}===: dn: {user_dn}, error: {res and 'None' or self.conn.result}"
        )

    def enable_user(self, dn):
        res = self.conn.modify(
            dn, {"userAccountControl": [(ldap3.MODIFY_REPLACE, 512)]}
        )
        logger.info(
            f"=== Enable user {res and 'success' or 'failed'}===: dn: {dn}, error: {res and 'None' or self.conn.result}"
        )

    def gen_user_dn_in_ou(self, user: json, ou: str):
        """
        理论上cn取自scim userName，Scim Server应该保证userName不会重名
        如果当前ou下不存在同名cn，不需要重新生成cn，
        如果当前ou下存在同名cn：
            在当前ou下此用户之前同步过， 不需要重新生成cn
        """
        user_cn = user["cn"]
        user_dn = f"CN={user_cn},{ou}"

        return_flag = False
        if not self.exists_user_dn(user_dn):
            return_flag = True

        if not return_flag:
            ldap_user = self.get_user_from_ldap_by_id(user["id"])
            if ldap_user:
                ldap_user_dn = ldap_user["dn"]
                _, ldap_user_ou = ldap_user_dn.split(",", 1)
                if ldap_user_ou.lower() == ou.lower():
                    return_flag = True

        if not return_flag:
            max_n = 1000
            cn = user_cn
            for n in range(1, max_n, 2):
                user_cn = cn + str(n)
                user_dn = f"cn={user_cn},{ou}"
                if not self.exists_user_dn(user_dn):
                    return_flag = True
                    break
                # logger.info(f"user_cn: {user_cn} exists for {user['name']}")

        if not return_flag:
            raise Exception(
                "more than {max_n} duplicate email: {mail} exists for {user['name']}"
            )

        user["ldap_cn"] = user_cn
        user["ldap_dn"] = user_dn
        # logger.debug(f"{user_dn} generated for user {user['name']} user_id{user['id']}")

    def gen_group_dn(self, group: json, parent_group: json):
        # group["ldap_cn"] = self.group_name_prefix + group["name"]
        group["ldap_cn"] = group["name"]
        if parent_group:
            # group_last_name = group["ldap_cn"].split("_")[-1]
            # group["ldap_ou"] = f"ou={group_last_name},{parent_group['ldap_ou']}"
            group["ldap_ou"] = f"OU={group['name']},{parent_group['ldap_ou']}"
        else:
            group["ldap_ou"] = f"OU={group['name']},{self.root_dn}"
        # group["ldap_dn"] = f"cn={group['ldap_cn']},{group['ldap_ou']}"

    def exists_user_dn(self, dn: str):
        search_base = dn
        search_filter = f"(objectclass={self.user_object_class})"
        res = self.conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
        )
        if not res or not json.loads(self.conn.response_to_json())["entries"]:
            return False
        return True

    # def exists_group_dn(self, dn: str):
    #     search_base = dn
    #     search_filter = f"(objectclass={self.group_object_class})"
    #     res = self.conn.search(
    #         search_base=search_base,
    #         search_filter=search_filter,
    #         search_scope=ldap3.SUBTREE,
    #     )
    #     if not res or not json.loads(self.conn.response_to_json())["entries"]:
    #         return False
    #     return True

    def exists_ou_dn(self, dn: str):
        search_base = dn
        search_filter = f"(objectclass={self.ou_object_class})"
        res = self.conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=ldap3.BASE,
        )
        if not res or not json.loads(self.conn.response_to_json())["entries"]:
            return False
        return True

    def get_user_from_ldap_by_id(self, user_id: str):
        search_filter = (
            f"(&(objectclass={self.user_object_class})({self.match_attr}={user_id}))"
        )
        res = self.conn.search(
            search_base=self.root_dn,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
            attributes=ldap3.ALL_ATTRIBUTES,
            size_limit=1,
        )
        if res:
            entries = json.loads(self.conn.response_to_json())["entries"]
            if entries:
                result = entries[0]
                return result
        return None

    # def get_group_from_ldap_by_id(self, group_id: str):
    #     search_base = self.search_base
    #     search_filter = (
    #         f"(&(objectclass={self.group_object_class})(sAMAccountName={group_id}))"
    #     )
    #     res = self.conn.search(
    #         search_base=search_base,
    #         search_filter=search_filter,
    #         search_scope=ldap3.SUBTREE,
    #         attributes=ldap3.ALL_ATTRIBUTES,
    #         size_limit=1,
    #     )
    #     if not res:
    #         return None
    #     entries = json.loads(self.conn.response_to_json())["entries"]
    #     if not entries:
    #         return None
    #     return entries[0]

    # def get_group_under_ou(self, ou: str):
    #     search_base = ou
    #     search_filter = f"(objectclass={self.group_object_class})"
    #     res = self.conn.search(
    #         search_base=search_base,
    #         search_filter=search_filter,
    #         search_scope=ldap3.LEVEL,
    #         size_limit=1,
    #     )
    #     if not res:
    #         return None
    #     entries = json.loads(self.conn.response_to_json())["entries"]
    #     if not entries:
    #         return None
    #     return entries[0]

    def get_all_ou_from_ldap(self):
        search_base = self.root_dn
        search_filter = f"(objectclass={self.ou_object_class})"
        res = self.conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
        )
        if not res:
            return []
        all_ou = json.loads(self.conn.response_to_json())["entries"]
        all_ou_dn = [x["dn"] for x in all_ou]
        index = [x.lower() for x in all_ou_dn].index(self.root_dn.lower())
        del all_ou_dn[index]
        return all_ou_dn

    def get_all_user_from_ldap(self):
        search_base = self.root_dn
        search_filter = f"(objectclass={self.user_object_class})"
        res = self.conn.extend.standard.paged_search(
            search_base=self.root_dn,
            search_filter=search_filter,
            search_scope=ldap3.SUBTREE,
            paged_size=50,
            attributes=ldap3.ALL_ATTRIBUTES,
        )
        if not res:
            return []
        all_user_dn = [user["dn"] for user in res]
        return all_user_dn

    def move_user(self, source_dn, destination_dn):
        relative_dn, new_superior = destination_dn.split(",", 1)
        res = self.conn.modify_dn(
            dn=source_dn,
            relative_dn=relative_dn,
            delete_old_dn=True,
            new_superior=new_superior,
        )
        logger.debug(
            f"move user {res and 'success' or 'failed'} from {source_dn} to {destination_dn}, error: {res and 'None' or self.conn.result}"
        )

    def move_group(self, source_dn, destination_dn):
        relative_dn, new_superior = destination_dn.split(",", 1)
        res = self.conn.modify_dn(
            dn=source_dn,
            relative_dn=relative_dn,
            delete_old_dn=True,
            new_superior=new_superior,
        )
        logger.debug(
            f"move group {res and 'success' or 'failed'} from {source_dn} to {destination_dn}, error: {res and 'None' or self.conn.result}"
        )

    def move_user_to_ou(self, user: json, source_dn, dest_ou: str):
        _, source_ou = source_dn.split(",", 1)
        if source_ou.lower() != dest_ou.lower():
            self.gen_user_dn_in_ou(user, dest_ou)
            user_dn = user["ldap_dn"]
            self.move_user(source_dn=source_dn, destination_dn=user_dn)

    def compare_user(self, user: json, ldap_user: json):
        user_attributes = user["attributes"]
        ldap_user_attributes = ldap_user["attributes"]
        new_value = {}
        old_value = {}
        compare_keys = [
            "givenName",
            "sn",
            "displayName",
            # "title",
            # "department",
            # "company",
            # "pager",
        ]
        for k in compare_keys:
            if k in user_attributes and user_attributes[k] != ldap_user_attributes.get(
                k
            ):
                new_value[k] = user_attributes[k]
                old_value[k] = ldap_user_attributes.get(k)

        return new_value, old_value

    def update_user(self, user_dn: str, new_value: json, old_value: json):
        changes = {}
        for k, v in new_value.items():
            changes[k] = [(ldap3.MODIFY_REPLACE, v)]
        res = self.conn.modify(dn=user_dn, changes=changes)
        logger.info(
            f"=== updating user {res and 'success' or 'failed'}: {user_dn}, updated_data: {new_value}, old_data: {old_value}, error: {res and 'None' or self.conn.result} ==="
        )

    # def add_group(self, group: json):
    #     cn = group["ldap_cn"]
    #     dn = group["ldap_dn"]
    #     group_id = group["id"]
    #     if len(cn) > 64:
    #         logger.info(f"group {group_id} name: {cn} too long, more than 64")
    #         return

    #     object_class = self.group_object_class
    #     attributes = {
    #         "cn": cn,
    #         "groupType": "-2147483646",
    #         "sAMAccountName": group_id,
    #     }
    #     res = self.conn.add(dn=dn, object_class=object_class, attributes=attributes)
    #     logger.debug(
    #         f"add group {res and 'success' or 'failed'}: dn: {dn}, object_class: {object_class}, attributes: {attributes}, error: {res and 'None' or self.conn.result}"
    #     )

    def add_ou(self, dn: str):
        object_class = self.ou_object_class
        attributes = None
        res = self.conn.add(dn=dn, object_class=object_class, attributes=attributes)
        logger.debug(
            f"add ou {res and 'success' or 'failed'}: dn: {dn}, object_class: {object_class}, attributes: {attributes}, error: {res and 'None' or self.conn.result}"
        )
        self.sync_log.groups_created += 1

    def set_ou_manager(self, ou_dn: str, manager_id: str):
        manager = self.user_dict.get(manager_id)
        if not manager:
            return
        if manager["status"] == "enabled":
            changes = {"managedBy": [(ldap3.MODIFY_REPLACE, [manager["ldap_dn"]])]}
        else:
            changes = {"managedBy": [(ldap3.MODIFY_DELETE, [])]}
        self.conn.modify(dn=ou_dn, changes=changes)

    def get_user_group(self, user):
        group_id = user["group_id"]
        group = self.group_dict.get(group_id)
        return group

    def get_user_ou(self, user):
        group = self.get_user_group(user)
        if not group:
            logger.debug(f"user_id {user['id']} does not belong to a group")
            ou = self.root_dn
        else:
            ou = group["ldap_ou"]
        user["ldap_ou"] = ou
        return ou

    # def add_group_member(self, dn, group_dn):
    #     res = self.conn.extend.microsoft.add_members_to_groups(dn, group_dn)
    #     if not res:
    #         logger.error(
    #             f"add dn: {dn} to group: {group_dn} failed, error: {self.conn.result}"
    #         )

    # def remove_group_member(self, dn, group_dn):
    #     res = self.conn.extend.microsoft.remove_members_from_groups(dn, group_dn)
    #     if not res:
    #         logger.error(
    #             f"remove dn: {dn} from group: {group_dn} failed, error: {self.conn.result}"
    #         )

    # def remove_member_of_attr(self, ldap_object):
    #     # remove user or group from group by ldap memberOf attribute
    #     attrs = ldap_object.get("attributes", {})
    #     dn = attrs.get("distinguishedName", "")
    #     if not dn:
    #         return

    #     groups_dn = attrs.get("memberOf", [])
    #     for group_dn in groups_dn:
    #         if self.exists_group_dn(group_dn) and group_dn not in self.exclude_groups:
    #             self.remove_group_member(dn, group_dn)

    # def remove_member_of_group(self, ldap_object):
    #     # remove user or group from group by ldap member attribute
    #     attrs = ldap_object.get("attributes", {})
    #     dn = attrs.get("distinguishedName", "")
    #     if not dn:
    #         return

    #     members_dn = attrs.get("member", [])
    #     self.remove_group_member(members_dn, dn)

    def get_root_groups(self):
        none_root_groups = set()
        for group in self.groups:
            # if group["status"] == "enabled":
            members = group.get("members", [])
            for member in members:
                none_root_groups.add(member["value"])

        root_groups = [
            group for group in self.groups if group["id"] not in none_root_groups
        ]
        return root_groups

    def sync_groups_from_root(self, group, parent_group=None):
        self.gen_group_dn(group, parent_group)

        if parent_group:
            group["parent"] = parent_group

        if not self.exists_ou_dn(group["ldap_ou"]):
            self.add_ou(group["ldap_ou"])

        parent_group = group
        for member in group.get("members", []):
            child_group_id = member["value"]
            child_group = self.group_dict[child_group_id]
            # if child_group["status"] == "enabled":
            self.sync_groups_from_root(child_group, parent_group=parent_group)

    def sync_groups(self):
        logger.info(
            "========================= Syncing Groups ========================="
        )
        self.group_dict = {group["id"]: group for group in self.groups}

        # sync from root group to leaf group
        root_groups = self.get_root_groups()
        logger.info(f"root_groups found: {[group['id'] for group in root_groups]}")
        for root_group in root_groups:
            logger.info(f"syncing group from root_group: {root_group['id']}")
            self.sync_groups_from_root(root_group)

    def delete_ou(self, ou_dn):
        # 递归删除 ou
        search_base = ou_dn
        search_filter = "(objectclass=*)"
        attributes = ldap3.ALL_ATTRIBUTES
        res = self.conn.search(
            search_base=search_base,
            search_filter=search_filter,
            search_scope=ldap3.LEVEL,
            attributes=attributes,
        )

        # ou 不存在或已被删除或到了叶子节点
        if not res:
            # 叶子节点
            if ou_dn not in self.deleted_ou_dn:
                res = self.conn.delete(ou_dn)
                self.deleted_ou_dn.add(ou_dn)
                logger.info(
                    f"delete ou {res and 'success' or 'failed'}: dn: {ou_dn}, error: {res and 'None' or self.conn.result}"
                )
            return

        entries = json.loads(self.conn.response_to_json())["entries"]
        for entry in entries:
            if (
                self.ou_object_class in entry["attributes"]["objectClass"]
                and entry["dn"] in self.delete_ou_dn
            ):
                self.delete_ou(entry["dn"])
            if self.group_object_class in entry["attributes"]["objectClass"]:
                res = self.conn.delete(entry["dn"])
                logger.debug(
                    f"delete group {res and 'success' or 'failed'}: dn: {entry['dn']}, error: {res and 'None' or self.conn.result}"
                )
            if self.user_object_class in entry["attributes"]["objectClass"]:
                logger.debug(f"move user {entry['dn']} out of deleted ou")
                user = {
                    "id": entry["attributes"]["employeeID"],
                    "name": entry["attributes"]["name"],
                }
                self.move_user_to_ou(user, source_dn=entry["dn"], dest_ou=self.root_dn)

        if ou_dn not in self.deleted_ou_dn:
            res = self.conn.delete(ou_dn)
            self.deleted_ou_dn.add(ou_dn)
            logger.debug(
                f"delete ou {res and 'success' or 'failed'}: dn: {ou_dn}, error: {res and 'None' or self.conn.result}"
            )

    def delete_ous(self):
        logger.info("deleting orgnazationalUnits")
        all_ou_dn = self.get_all_ou_from_ldap()

        enabled_ou_dn = set(group["ldap_ou"].lower() for group in self.groups)
        self.delete_ou_dn = [ou for ou in all_ou_dn if ou.lower() not in enabled_ou_dn]
        self.deleted_ou_dn = set()
        logger.info(f"ou to be deleted: {self.delete_ou_dn}")
        for dn in self.delete_ou_dn:
            self.delete_ou(dn)
            self.sync_log.groups_deleted += 1

    def sync_users(self):
        logger.info("========================= Syncing Users =========================")
        self.user_dict = {user["id"]: user for user in self.users}

        # sync users
        for user in self.users:
            # if user["active"]:
            # username may confict in the same ou
            ou = self.get_user_ou(user)
            self.gen_user_dn_in_ou(user, ou)

            ldap_user = self.get_user_from_ldap_by_id(user["id"])
            if not ldap_user:
                # add new user
                self.add_user(user)
            else:
                # move existing user
                user_dn = user["ldap_dn"]
                ldap_user_dn = ldap_user["dn"]
                _, source_ou = ldap_user_dn.split(",", 1)
                if source_ou.lower() != ou.lower():
                    self.move_user(source_dn=ldap_user_dn, destination_dn=user_dn)
                else:
                    user["ldap_dn"] = ldap_user_dn
                new_value, old_value = self.compare_user(user, ldap_user)
                if new_value:
                    self.update_user(user["ldap_dn"], new_value, old_value)

            # if not user['active']:
            #     self.disable_user(user)
            # else:
            #     self.enable_user(user["ldap_dn"])

    def delete_users(self):
        all_user_dn = self.get_all_user_from_ldap()
        enabled_user_dn = set(user["ldap_dn"].lower() for user in self.users)
        self.delete_user_dn = [
            user for user in all_user_dn if user.lower() not in enabled_user_dn
        ]
        self.deleted_user_dn = set()
        logger.info(f"User to be deleted: {self.delete_user_dn}")
        for dn in self.delete_user_dn:
            res = self.conn.delete(dn)
            self.sync_log.users_deleted += 1
            self.deleted_user_dn.add(dn)
            logger.info(
                f"=== Delete user {res and 'success' or 'failed'}: dn: {dn}, error: {res and 'None' or self.conn.result}"
            )

    def disable_user(self, user):
        logger.info(f"=== Disabling user: id {user['id']} name user['name'] ===")
        ldap_user = self.get_user_from_ldap_by_id(user["id"])
        if not ldap_user:
            logger.warning(
                f"=== Disabling user {user['id']}, but {user['id']} does not exist in ldap ==="
            )
            return
        ldap_user_dn = ldap_user["dn"]

        res = self.conn.modify(
            ldap_user_dn, {"userAccountControl": [(ldap3.MODIFY_REPLACE, 514)]}
        )
        logger.info(
            f"=== Disable user {res and 'success' or 'failed'}===: dn: {ldap_user_dn}, error: {res and 'None' or self.conn.result}"
        )

    def sync(self):
        self.sync_groups()
        self.sync_users()
        self.delete_users()
        self.delete_ous()
