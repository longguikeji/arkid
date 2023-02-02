from email.headerregistry import Group
from email.mime import base
from ninja import Field
from typing import Optional
from types import SimpleNamespace
from arkid.core import event
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.translation import gettext_default as _
from arkid.core.extension.scim_sync import (
    BaseScimSyncClientSchema,
    BaseScimSyncServerSchema,
    ScimSyncExtension,
)
from arkid.common.logger import logger
from arkid.core.models import UserGroup, User, Tenant
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.core2_group import Core2Group
from scim_server.protocol.path import Path
from scim_server.utils import (
    compose_core2_user,
    compose_enterprise_extension,
    compose_core2_group,
    compose_core2_group_member,
)
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from scim_server.schemas.member import Member
from scim_server.schemas.user_groups import UserGroup as ScimUserGroup
from django.db.utils import IntegrityError
from scim_server.exceptions import NotImplementedException
from .constants import *

import requests
import time


WeChatWorkClientConfig = create_extension_schema(
    "WeChatWorkClientConfig",
    __file__,
    fields=[
        ('corpid', str, Field(title=_("CorpID", "CorpID"))),
        ('corpsecret', str, Field(title=_("CorpSecret", "CorpSecret"))),
        ('syncsecret', str, Field(title=_("SyncSecret", "SyncSecret"))),
    ],
    base_schema=BaseScimSyncClientSchema,
)

WeChatWorkServerConfig = create_extension_schema(
    "WeChatWorkServerConfig",
    __file__,
    fields=[
        ('corpid', str, Field(title=_("CorpID", "CorpID"))),
        ('corpsecret', str, Field(title=_("CorpSecret", "CorpSecret"))),
    ],
    base_schema=BaseScimSyncServerSchema,
)


class ScimSyncWeChatWorkExtension(ScimSyncExtension):

    def load(self):
        self.register_scim_sync_schema('WeChatWork', WeChatWorkClientConfig, WeChatWorkServerConfig)
        super().load()

    def group_recursive_order(self, group, group_dict):
        '''
        递归进行分组排序
        '''
        group_members = group.get("members", [])
        children = []
        for group_member in group_members:
            group_child_item = group_dict.get(group_member.get('value'))
            self.group_recursive_order(group_child_item, group_dict)    
            group_child_item['is_del'] = True
            children.append(group_child_item)
        group['children'] = children
        # 去掉多余的数据，精简数据
        if "schemas" in group:
            group.pop("schemas")
        if "externalId" in group:
            group.pop("externalId")
        # if "members" in group:
        #     group.pop("members")
        if "meta" in group:
            group.pop("meta")
        if "displayName" in group:
            displayName = group.pop("displayName")
            group["name"] = displayName

    def group_recursive_create(self, group, access_token, parent_dept_id, is_first=True, create_access_token=''):
        '''
        递归分组创建
        '''
        if is_first:
            # 默认为根节点(不能不从根节点走)
            parent_dept_id = str(1)
        # 获取指定部门的子部门
        child_depts = []
        temp_child_depts = self.get_all_dept(access_token, parent_dept_id)
        for temp_child_dept in temp_child_depts:
            parentid = temp_child_dept.get('parentid', 0)
            if int(parentid) == int(parent_dept_id):
                child_depts.append(temp_child_dept)
        child_dept_name_dict = {}
        for child_dept in child_depts:
            child_dept_name = child_dept.get('name', '')
            if child_dept_name:
                child_dept_name_dict[child_dept_name] = child_dept
        if is_first:
            # 对于首项要单独处理创建
            name = group.get('name', '')
            if name not in child_dept_name_dict:
                dept_id = self.create_http_dept(create_access_token, name, parent_dept_id)
            else:
                dept_id = child_dept_name_dict.get(name).get('id', '0')
            parent_dept_id = dept_id
            group['real_id'] = dept_id
            # 重新计算
            child_depts = []
            child_dept_name_dict = {}
            child_depts = self.get_all_dept(access_token, parent_dept_id)
            for child_dept in child_depts:
                child_dept_name = child_dept.get('name', '')
                if child_dept_name:
                    child_dept_name_dict[child_dept_name] = child_dept
        # 更新子部门
        for group_child in group.get('children',[]):
            # 新建部门
            name = group_child.get('name', '')
            if name not in child_dept_name_dict:
                # 如果没在已有的部门
                dept_id = self.create_http_dept(create_access_token, name, parent_dept_id)
            else:
                # 如果在已有的部门
                child_dept = child_dept_name_dict.get(name)
                dept_id = child_dept.get('id', -1)
            group_child['real_id'] = dept_id
            # 继续遍历子部门
            self.group_recursive_create(group_child, access_token, dept_id, False, create_access_token)

    def sync(self, config, sync_log):
        """
        Args:
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info(
            f"============= Sync Start With Config: {config}/{config.config} ================"
        )
        groups, users = self.get_groups_users(config)
        if not groups or not users:
            return
        items = self.sync_groups(groups, config, sync_log)
        self.sync_users_groups(users, items, config, sync_log)


    def sync_groups(self, groups, config, sync_log):
        """
        遍历groups中的SCIM 组织，逐一和ArkID中的组织匹配，如果不存在就创建，存在则更新，在此过程中
        同时遍历每个SCIM 组织中的members，同样的方式在ArkID中创建或更新组织，并且维护组织之间的父子关系，
        最后删除以前同步到ArkID但不在本次同步数据中的组织
        Args:
            groups (List): SCIM Server返回的组织列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info("###### update&create groups ######")
        # groups = [
        #     {
        #         "schemas":[
        #             "urn:ietf:params:scim:schemas:core:2.0:Group"
        #         ],
        #         "id":"110",
        #         "externalId":None,
        #         "displayName":"测试部门",
        #         "members":[
        #             {
        #                 "value":"111",
        #                 "ref":None,
        #                 "type":None
        #             }
        #             ,
        #             {
        #                 "value":"114",
        #                 "ref":None,
        #                 "type":None
        #             }
        #         ],
        #         "meta":{
        #             "resourceType":"Group",
        #             "created":None,
        #             "lastModified":None,
        #             "location":None,
        #             "version":None
        #         }
        #     },
        #     {
        #         "schemas":[
        #             "urn:ietf:params:scim:schemas:core:2.0:Group"
        #         ],
        #         "id":"111",
        #         "externalId":None,
        #         "displayName":"研发和产品",
        #         "members":[
        #             {
        #                 "value":"112",
        #                 "ref":None,
        #                 "type":None
        #             },
        #             {
        #                 "value":"113",
        #                 "ref":None,
        #                 "type":None
        #             }
        #         ],
        #         "meta":{
        #             "resourceType":"Group",
        #             "created":None,
        #             "lastModified":None,
        #             "location":None,
        #             "version":None
        #         }
        #     },
        #     {
        #         "schemas":[
        #             "urn:ietf:params:scim:schemas:core:2.0:Group"
        #         ],
        #         "id":"112",
        #         "externalId":None,
        #         "displayName":"研发",
        #         "members":[
        #         ],
        #         "meta":{
        #             "resourceType":"Group",
        #             "created":None,
        #             "lastModified":None,
        #             "location":None,
        #             "version":None
        #         }
        #     },
        #     {
        #         "schemas":[
        #             "urn:ietf:params:scim:schemas:core:2.0:Group"
        #         ],
        #         "id":"113",
        #         "externalId":None,
        #         "displayName":"产品",
        #         "members":[

        #         ],
        #         "meta":{
        #             "resourceType":"Group",
        #             "created":None,
        #             "lastModified":None,
        #             "location":None,
        #             "version":None
        #         }
        #     }
        #     ,
        #     {
        #         "schemas":[
        #             "urn:ietf:params:scim:schemas:core:2.0:Group"
        #         ],
        #         "id":"114",
        #         "externalId":None,
        #         "displayName":"设计",
        #         "members":[

        #         ],
        #         "meta":{
        #             "resourceType":"Group",
        #             "created":None,
        #             "lastModified":None,
        #             "location":None,
        #             "version":None
        #         }
        #     }
        # ]
        # 准备一个部门字典
        group_dict = {}
        for group in groups:
            group_id = group.get("id", "0")
            group_dict[group_id] = group
        # 将子部门放入父部门里
        for group in group_dict.values():
            self.group_recursive_order(group, group_dict)
        temp_group = []
        for group in group_dict.values():
            is_del = group.get("is_del", False)
            if not is_del:
                temp_group.append(group)
        # 取得access_token
        access_token = self.get_http_access_token(config.config)
        sync_access_token = self.get_http_access_token(config.config, is_sync=True)
        # 创建分组(1表示根节点)
        for group in temp_group:
            self.group_recursive_create(group, access_token, 1, True, sync_access_token)
        # 需要知道那些部门更新了，那些部门没更新，没更新的要删除掉
        exists_depts_ids = []
        for group in temp_group:
            real_id = group.get('real_id', -1)
            if real_id != -1:
                child_depts_1 = self.get_http_all_depts(access_token, real_id)
                for child_depts_item in child_depts_1:
                    dept_id = child_depts_item.get('id', -1)
                    exists_depts_ids.append(dept_id)
        items = []
        for temp_item in temp_group:
            self.unpack_group_dict(temp_item, items)
        real_depts_ids = []
        for item in items:
            real_id = item.get('real_id', -1)
            if real_id != -1:
                real_depts_ids.append(real_id)
        delete_ids = []
        for exists_depts_id in exists_depts_ids:
            if exists_depts_id not in real_depts_ids:
                delete_ids.append(exists_depts_id)
        # print(delete_ids)
        for delete_id in delete_ids:
            self.delete_http_dept(sync_access_token, delete_id)
        return items

    def sync_users(self, users, config, sync_log):
        """
        保留方法不需要实现
        """
        logger.info("###### update&create users ######")

    def sync_users_groups(self, users, items, config, sync_log):
        """
        遍历users中的SCIM 用户记录，逐一和ArkID中的用户匹配，如果不存在匹配的就创建，存在则更新，
        最后删除以前同步到ArkID但不在本次同步数据中的用户(如果没有手机号就不能同步，而且手机号必须唯一)
        Args:
            users (List): SCIM Server返回的用户列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info("###### update&create users ######")
        # 取得access_token
        access_token = self.get_http_access_token(config.config)
        sync_access_token = self.get_http_access_token(config.config, is_sync=True)
        # print(123456)
        # print(json.dumps(users, ensure_ascii=False))
        # users = [
        #     {
        #         "schemas":[
        #             "urn:ietf:params:scim:schemas:core:2.0:User",
        #             "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
        #         ],
        #         "id":"hanbin",
        #         "externalId":None,
        #         "userName":"hanbin",
        #         "name":None,
        #         "displayName":"测试人员",
        #         "nickName":None,
        #         "profileUrl":None,
        #         "title":None,
        #         "userType":None,
        #         "preferredLanguage":None,
        #         "locale":None,
        #         "timezone":None,
        #         "active":True,
        #         "password":None,
        #         "emails":None,
        #         "phoneNumbers":[
        #             {
        #                 "type":"work",
        #                 "primary":None,
        #                 "value":"13800138001"
        #             }
        #         ],
        #         "ims":None,
        #         "photos":None,
        #         "address":None,
        #         "groups":[
        #             {
        #                 "type":None,
        #                 "primary":None,
        #                 "value":113,
        #                 "ref":None,
        #                 "display":"产品"
        #             },
        #             {
        #                 "type":None,
        #                 "primary":None,
        #                 "value":114,
        #                 "ref":None,
        #                 "display":"设计"
        #             }
        #         ],
        #         "roles":None,
        #         "meta":{
        #             "resourceType":"User",
        #             "created":None,
        #             "lastModified":None,
        #             "location":None,
        #             "version":None
        #         },
        #         "enterprise_extension":{
        #             "employeeNumber":None,
        #             "costCenter":None,
        #             "organization":None,
        #             "division":None,
        #             "department":None,
        #             "manager":None
        #         }
        #     }
        # ]
        items_dict = {}
        real_ids = []
        for item in items:
            item_id = int(item.get('id', 1))
            real_id = item.get('real_id', '')
            items_dict[item_id] = item
            if real_id:
                real_ids.append(real_id)
        # 进行用户同步工作
        for user in users:
            name = user.get('displayName', '')
            phoneNumbers = user.get('phoneNumbers', [])
            mobile = ''
            for phoneNumber in phoneNumbers:
                mobile = phoneNumber.get('value', '')
                groups = user.get('groups', [])
                if name and mobile:
                    # 只有有名称和手机号才能新建用户
                    values = []
                    for group in groups:
                        value = group.get('value', None)
                        if value:
                            values.append(value)
                    if values:
                        dept_id_list = []
                        # 新建用户
                        for value in values:
                            # 取得对应部门id
                            dept_item = items_dict.get(value, None)
                            if dept_item:
                                dept_id = dept_item.get('real_id', None)
                                if dept_id:
                                    dept_id_list.append(dept_id)
                        if dept_id_list:
                            userid = self.get_http_by_mobile_user(access_token, mobile)
                            if userid:
                                # 根据用户id获取用户信息
                                user_obj = self.get_http_user(access_token, userid)
                                user_dept_id_list = user_obj.get('department', [])
                                user_dept_id_temp_list = []
                                for user_dept_id in user_dept_id_list:
                                    # 除去scim服务端提供的部门id，其余的就是自带的
                                    if user_dept_id not in real_ids:
                                        user_dept_id_temp_list.append(user_dept_id)
                                # 这是现在用户的部门id
                                user_dept_id_temp_list.extend(dept_id_list)
                                self.update_http_user_dept(sync_access_token, userid, user_dept_id_temp_list)
                            else:
                                # 如果不存在用户就新建
                                self.create_http_user(sync_access_token, name, mobile, dept_id_list)

    def unpack_group_dict(self, temp_item, items):
        '''
        解开分组字典
        '''
        children = temp_item.pop('children')
        if temp_item not in items:
            items.append(temp_item)
        for item in children:
            self.unpack_group_dict(item, items)

    def create_http_dept(self, access_token, name='', parent_id=1):
        '''
        创建钉钉部门
        '''
        url = CREATE_DEPT_URL.format(access_token)

        params = {
            "name": name,
            "parentid": parent_id,
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        if errmsg != "created":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        dept_id = response.get('id', 0)
        return dept_id

    def delete_http_dept(self, access_token, delete_id):
        '''
        删除企业微信部门
        '''
        url = DELETE_DEPT_URL.format(access_token, str(delete_id))

        response = requests.get(url).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        if errmsg != "deleted":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        return True

    def create_http_user(self, access_token, name, mobile, dept_id_list):
        '''
        创建用户
        '''
        url = CREATE_USER_URL.format(access_token)

        params = {
            'name': name,
            'userid': mobile,
            'mobile': mobile,
            'department': dept_id_list,
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        if errmsg != "created":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        return True

    def get_http_by_mobile_user(self, access_token, mobile):
        '''
        根据手机号查询用户ID
        '''
        url = USER_MOBILE_URL.format(access_token)

        params = {
            'mobile': str(mobile)
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        if errcode == 46004:
            return ''
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        userid = response.get('userid', '')
        return userid

    def update_http_user_dept(self, access_token, userid, dept_id_list):
        '''
        修改用户部门
        '''
        url = UPDATE_USER_URL.format(access_token)
        params = {
            'userid': userid,
            'department': dept_id_list
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        if errmsg != "updated":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        return True

    def get_http_user(self, access_token, userid):
        '''
        根据用户id获取用户信息
        '''
        url = GET_USER_URL.format(access_token, userid)
        response = requests.get(url).json()
        errmsg = response.pop("errmsg", "ok")
        errcode = response.pop("errcode", 0)
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        return response

    ############################################################################
    # FeiShu Server
    ############################################################################

    def get_http_access_token(self, config, is_sync=False):
        '''
        获取企业微信access_token
        '''
        corpid = config.get('corpid', '')
        corpsecret = config.get('corpsecret', '')
        if is_sync:
            syncsecret = config.get('syncsecret', '')
            corpsecret = syncsecret
        url = TOKEN_URL.format(corpid, corpsecret)
        response = requests.get(url).json()

        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        # print('-----get wechatwork scim token-----')
        # print(response)
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        access_token = response.get('access_token', '')
        return access_token
    
    def get_http_all_depts(self, access_token, parent_id=None):
        '''
        获取所有部门
        '''
        url = DEPT_URL.format(access_token)
        if parent_id:
            url = '{}&id={}'.format(url, parent_id)
        response = requests.get(url).json()

        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        # print('-----get wechatwork scim token-----')
        # print(response)
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        department = response.get('department', [])
        return department

    def get_http_all_users(self, access_token, department_id):
        '''
        获取所有用户
        '''
        url = USER_URL.format(access_token, department_id)
        response = requests.get(url).json()

        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", 0)
        # print('-----get wechatwork scim token-----')
        # print(response)
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        userlist = response.get('userlist', [])
        return userlist

    def get_all_dept(self, access_token, parent_id=None):
        '''
        获取所有部门
        '''
        all_depts = self.get_http_all_depts(access_token, parent_id)
        if all_depts and parent_id:
            items = []
            for dept in all_depts:
                dept_id = dept.get('id')
                if dept_id != parent_id:
                    items.append(dept)
            return items
        else:
            return all_depts
    
    def get_all_user(self, access_token, dept_id):
        '''
        获取所有用户
        '''
        all_users = self.get_http_all_users(access_token, dept_id)
        return all_users

    def get_users(self, config):
        '''
        获取用户
        '''
        dept_list = []
        user_list = []
        access_token = self.get_http_access_token(config)
        # 需要先获取公司基础信息
        # base_dept = self.get_http_dept(access_token, 0)
        # dept_list.append({
        #     'name': base_dept.get('name', ''),
        #     'open_department_id': base_dept.get('open_department_id', '0'),
        # })
        # 获取所有部门
        dept_list = self.get_all_dept(access_token)
        # 获取所有用户
        for dept in dept_list:
            dept_id = dept.get('id', '1')
            all_users = self.get_all_user(access_token, dept_id)
            if all_users:
                user_list.extend(all_users)
            # self.get_recursive_users(access_token, user_list, dept_id, 0)
        return user_list, dept_list
    
    def get_group(self, config):
        '''
        获取分组
        '''
        dept_list = []
        access_token = self.get_http_access_token(config)
        # 需要先获取公司基础信息
        # base_dept = self.get_http_dept(access_token, 0)
        # corp = self.get_http_corp(access_token)
        # corp_name = corp.get('name', '')
        # if corp_name and base_dept.get('name', '') == '':
        #     base_dept['name'] = corp_name
        # dept_list.append({
        #     'name': base_dept.get('name', ''),
        #     'open_department_id': base_dept.get('open_department_id', '0'),
        # })
        # 获取所有部门
        dept_list = self.get_all_dept(access_token)
        dept_dict = {}
        for dept_item in dept_list:
            dept_item['children'] = []
            dept_dict[dept_item.get('id', '1')] = dept_item

        for dept_item in dept_list:
            parent_id = dept_item.get('parentid', 0)
            if parent_id != 0:
                dept_obj = dept_dict.get(parent_id)
                children = dept_obj.get('children', [])
                children.append(dept_item.get('id', "1"))
                dept_obj['children'] = children
        return dept_list

    def _get_scim_user(self, feishu_user):
        attr_map = {"userid": "id", "active": "active", "username": "userName", "name":"displayName"}
        scim_user = Core2EnterpriseUser(userName='', groups=[])
        for arkid_attr, scim_attr in attr_map.items():
            value = feishu_user.get(arkid_attr, '')
            scim_path = Path.create(scim_attr)
            if (
                scim_path.schema_identifier
                and scim_path.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser
            ):
                compose_enterprise_extension(scim_user, scim_path, value)
            else:
                compose_core2_user(scim_user, scim_path, value)

        # 生成用户所在的组
        depts = feishu_user.get('depts',[])
        for dept in depts:
            scim_group = ScimUserGroup()
            scim_group.value = dept.get('id', 1)
            scim_group.display = dept.get('name', '')
            scim_user.groups.append(scim_group)
        return scim_user

    def _get_all_scim_users(self, config):
        scim_users = []
        # 获取所有用户开始
        feishu_users, dept_list = self.get_users(config)
        temp_feishu_users = []
        if feishu_users:
            for feishu_user in feishu_users:
                feishu_user_status = feishu_user.get('status', 1)
                if feishu_user_status == 1:
                    feishu_user_status = True
                else:
                    feishu_user_status = False
                temp_user = {
                    'dept_id_list': feishu_user.get('department', []),
                    'active': feishu_user_status,
                    'email': '',
                    'name': feishu_user.get('name', ''),
                    'mobile': '',
                    'username': feishu_user.get('userid', ''),
                    'userid': feishu_user.get('userid', '')
                }
                if temp_user not in temp_feishu_users:
                    temp_feishu_users.append(temp_user)
        feishu_users = temp_feishu_users
        # 部门转换为dict
        dept_dict = {}
        for dept_item in dept_list:
            dept_item_id = dept_item.get('id', "1")
            dept_dict[dept_item_id] = dept_item
        # 获取所有用户结束
        for feishu_user in feishu_users:
            dept_id_list = feishu_user.get('dept_id_list', [])
            depts = []
            for dept_id in dept_id_list:
                dept = dept_dict.get(dept_id, None)
                if dept:
                    dept_name = dept.get('name', '')
                    depts.append({
                        'id': dept_id,
                        'name': dept_name,
                    })
            feishu_user['depts'] = depts
            scim_user = self._get_scim_user(feishu_user)
            scim_users.append(scim_user)
        return scim_users

    def _get_scim_group(self, dept):
        attr_map = {"id": "id", "name": "displayName"}
        scim_group = Core2Group(displayName='')
        for arkid_attr, scim_attr in attr_map.items():
            value = dept.get(arkid_attr, '')
            scim_path = Path.create(scim_attr)
            compose_core2_group(scim_group, scim_path, value)
        for child in dept.get('children', []):
            member = Member()
            member.value = child
            scim_group.members.append(member)
        return scim_group

    def _get_all_scim_groups(self, config):
        scim_groups = []
        dept_list = self.get_group(config)
        for dept in dept_list:
            scim_group = self._get_scim_group(dept)
            scim_groups.append(scim_group)
        return scim_groups

    def query_users(self, request, parameters, correlation_identifier):
        """
        将ArkID中的用户转换成scim_server中的符合SCIM标准的Core2EnterpriseUser对象
        Args:
            request (HttpRequest): Django 请求
            parameters (scim_server.protocol.query_parameters.QueryParameters): Query请求对象
            correlation_identifier (str): 请求唯一标识
        Returns:
            List[Core2EnterpriseUser]: 返回scim_server模块中的标准用户对象列表
        """
        config_id = request.resolver_match.kwargs.get('config_id')
        config = self.get_config_by_id(config_id)
        if not parameters.alternate_filters:
            all_users = self._get_all_scim_users(config.config)
            return all_users

    def query_groups(self, request, parameters, correlation_identifier):
        """
        将ArkID中的组织转换成scim_server中的符合SCIM标准的Core2Group对象
        Args:
            request (HttpRequest): Django 请求
            parameters (scim_server.protocol.query_parameters.QueryParameters): Query请求对象
            correlation_identifier (str): 请求唯一标识
        Returns:
            List[Core2Group]: 返回scim_server模块中的标准组织对象列表
        """
        config_id = request.resolver_match.kwargs.get('config_id')
        config = self.get_config_by_id(config_id)
        if not parameters.alternate_filters:
            groups = self._get_all_scim_groups(config.config)
            return groups

    def create_user(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def create_group(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def delete_user(self, request, resource_identifier, correlation_identifier):
        raise NotImplementedException()

    def delete_group(self, request, resource_identifier, correlation_identifier):
        raise NotImplementedException()

    def replace_user(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def replace_group(self, request, resource, correlation_identifier):
        raise NotImplementedException()

    def retrieve_user(self, request, parameters, correlation_identifier):
        raise NotImplementedException()

    def retrieve_group(self, request, parameters, correlation_identifier):
        raise NotImplementedException()

    def update_user(self, request, patch, correlation_identifier):
        raise NotImplementedException()

    def update_group(self, request, patch, correlation_identifier):
        raise NotImplementedException()


extension = ScimSyncWeChatWorkExtension()
