from email.headerregistry import Group
from email.mime import base
from ninja import Field
from typing import Optional
from types import SimpleNamespace
from arkid.core import event
from arkid.core.extension import Extension, create_extension_schema
from arkid.core.event import SEND_SMS
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


DingDingClientConfig = create_extension_schema(
    "DingDingClientConfig",
    __file__,
    fields=[
        ('appkey', str, Field(title=_("AppKey", "AppKey"))),
        ('appsecret', str, Field(title=_("AppSecret", "AppSecret"))),
    ],
    base_schema=BaseScimSyncClientSchema,
)

DingDingServerConfig = create_extension_schema(
    "DingDingServerConfig",
    __file__,
    fields=[
        ('appkey', str, Field(title=_("AppKey", "AppKey"))),
        ('appsecret', str, Field(title=_("AppSecret", "AppSecret"))),
    ],
    base_schema=BaseScimSyncServerSchema,
)


class ScimSyncDingDingExtension(ScimSyncExtension):

    def load(self):
        self.register_scim_sync_schema('DingDing', DingDingClientConfig, DingDingServerConfig)
        super().load()

    def unpack_group_dict(self, temp_item, items):
        '''
        解开分组字典
        '''
        children = temp_item.pop('children')
        if temp_item not in items:
            items.append(temp_item)
        for item in children:
            self.unpack_group_dict(item, items)

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
        # 准备一个部门字典
        group_dict = {}
        group_ids = []
        for group in groups:
            group_id = group.get("id", "1")
            group_dict[group_id] = group
            group_ids.append('arkid:{}'.format(group_id))
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
        # print(access_token)
        # 创建分组(1表示根节点)
        for group in temp_group:
            self.group_recursive_create(group, access_token, "1", True)
        # 需要先获取公司基础信息
        base_dept_obj = {
            'dept_id': 1,
            'name': ''
        }
        dept_list = []
        # 获取所有部门
        self.get_recursive_depts(access_token, dept_list, base_dept_obj)
        # for dept_item in dept_list:
        #     if dept_item.get('dept_id') == 1:
        #         continue
        #     self.edit_http_dept(access_token, dept_item.get('dept_id', 1))
        # dept_list = []
        # self.get_recursive_depts(access_token, dept_list, base_dept_obj)
        # print(json.dumps(dept_list))
        # dingding会覆盖默认的source_identifier，所以需要重新写一次origin_id
        items = []
        for temp_item in temp_group:
            self.unpack_group_dict(temp_item, items)
        for index, group in enumerate(items):
            time.sleep(1)
            origin_id = 'arkid:{}'.format(group.get('id', ''))
            real_id = group.get('real_id', None)
            self.edit_http_dept(access_token, real_id, origin_id)
        # 改部门
        for group in temp_group:
            time.sleep(1)
            origin_id = 'arkid:{}'.format(group.get('id', ''))
            real_id = group.get('real_id', None)
            self.edit_http_dept(access_token, real_id, origin_id)
        # 需要把多余的部门删除掉
        dept_dict = {}
        for dept_item in dept_list:
            source_identifier = dept_item.get("source_identifier", "")
            if source_identifier and 'arkid:' in source_identifier:
                dept_dict[source_identifier] = dept_item
        # print(json.dumps(group_ids))
        for key, value in dept_dict.items():
            # print(key, value)
            if key not in group_ids:
                dept_id = value.get('dept_id', 1)
                # print('delete', dept_id)
                self.delete_http_dept(access_token, dept_id)

    def sync_users(self, users, config, sync_log):
        """
        遍历users中的SCIM 用户记录，逐一和ArkID中的用户匹配，如果不存在匹配的就创建，存在则更新，
        最后删除以前同步到ArkID但不在本次同步数据中的用户
        Args:
            users (List): SCIM Server返回的用户列表
            config (arkid.extension.models.TenantExtensionConfig): Client模式创建的配置
        """
        logger.info("###### update&create users ######")
        # 取得access_token
        access_token = self.get_http_access_token(config.config)
        # print(access_token)
        # 取得所有部门
        dept_list = []
        dept_dict = {}
        other_process_dept_ids = []
        self.get_recursive_depts(access_token, dept_list, {'dept_id': 1, 'name': ''})
        for dept_item in dept_list:
            source_identifier = dept_item.get('source_identifier', '')
            dept_id = dept_item.get('dept_id', 1)              
            if source_identifier and 'arkid:' in source_identifier:
                dept_dict[source_identifier] = dept_item
            else:
                other_process_dept_ids.append(dept_id)
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
                        group_id = 'arkid:{}'.format(value)
                        values.append(group_id)
                if values:
                    dept_id_list = []
                    # 新建用户
                    for value in values:
                        dept_item = dept_dict.get(value, None)
                        if dept_item:
                            dept_id = dept_item.get('dept_id', None)
                            if dept_id:
                                dept_id_list.append(dept_id)
                    if dept_id_list:
                        item_user = self.get_http_by_mobile_user(access_token, mobile)
                        if item_user:
                            # 如果已经存在就修改
                            userid = item_user.get('userid', '')
                            if userid:
                                # 根据用户id获取用户信息
                                user_obj = self.get_http_user(access_token, userid)
                                user_dept_id_list = user_obj.get('dept_id_list', [])
                                user_dept_id_temp_list = []
                                for user_dept_id in user_dept_id_list:
                                    if user_dept_id in other_process_dept_ids:
                                        user_dept_id_temp_list.append(user_dept_id)
                                user_dept_id_temp_list.extend(dept_id_list)
                                self.update_http_user_dept(access_token, userid, user_dept_id_temp_list)
                        else:
                            # 如果不存在用户就新建
                            self.create_http_user(access_token, name, mobile, dept_id_list)

    ############################################################################
    # DingDing Server
    ############################################################################

    def _get_scim_user(self, dingding_user):
        attr_map = {"userid": "id", "active": "active", "username": "userName", "mobile": "phoneNumbers[type eq work].value", "email":"emails[type eq work].value", "name":"displayName"}
        scim_user = Core2EnterpriseUser(userName='', groups=[])
        for arkid_attr, scim_attr in attr_map.items():
            value = dingding_user.get(arkid_attr, '')
            scim_path = Path.create(scim_attr)
            if (
                scim_path.schema_identifier
                and scim_path.schema_identifier == SchemaIdentifiers.Core2EnterpriseUser
            ):
                compose_enterprise_extension(scim_user, scim_path, value)
            else:
                compose_core2_user(scim_user, scim_path, value)

        # 生成用户所在的组
        depts = dingding_user.get('depts',[])
        for dept in depts:
            scim_group = ScimUserGroup()
            scim_group.value = dept.get('id', 1)
            scim_group.display = dept.get('name', '')
            scim_user.groups.append(scim_group)
        return scim_user

    def _get_scim_group(self, dept):
        attr_map = {"dept_id": "id", "name": "displayName"}
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
    
    def get_http_access_token(self, config):
        '''
        获取钉钉access_token
        '''
        appkey = config.get('appkey', '')
        appsecret = config.get('appsecret', '')
        url = TOKEN_URL.format(appkey, appsecret)
        response = requests.get(url).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        # print('-----get dingding scim token-----')
        # print(response)
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        access_token = response.get('access_token', '')
        return access_token
    
    def get_http_depts(self, access_token, dept_id=1):
        '''
        获取钉钉子部门
        '''
        url = DEPT_CHILD_URL.format(access_token)
        params = {
            'dept_id': dept_id
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', [])
        return result
    
    def get_http_dept(self, access_token, dept_id=1):
        '''
        获取钉钉部门详情
        '''
        url = DEPT_URL.format(access_token)
        params = {
            'dept_id': dept_id
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        return result

    def get_http_dept_ids(self, access_token, dept_id=1):
        '''
        获取钉钉子部门ID
        '''
        url = DEPT_CHILD_ID_URL.format(access_token)
        params = {
            'dept_id': dept_id
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        dept_id_list = result.get('dept_id_list', [])
        return dept_id_list
    
    def get_http_users(self, access_token, dept_id=1, size=100, cursor=0):
        '''
        获取钉钉用户
        '''
        url = USER_URL.format(access_token)
        params = {
            'dept_id': dept_id,
            'size': size,
            'cursor': cursor,
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        has_more = result.get('has_more', False)
        next_cursor = result.get('next_cursor', -1)
        result_list = result.get('list', [])
        return has_more, next_cursor, result_list

    def create_http_dept(self, access_token, name='', parent_id=1, origin_id='1'):
        '''
        创建钉钉部门
        '''
        url = CREATE_DEPT_URL.format(access_token)
        params = {
            'parent_id': parent_id,
            'name': name,
            # 唯一标识(为了便于和用户那边做关联)
            "source_identifier": origin_id
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        dept_id = result.get('dept_id', -1)
        return dept_id

    def edit_http_dept(self, access_token, dept_id=1, origin_id=''):
        '''
        更新钉钉部门
        '''
        url = EDIT_DEPT_URL.format(access_token)
        params = {
            'dept_id': dept_id,
            "source_identifier": origin_id
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        request_id = response.get('request_id', "")
        return request_id
    
    def delete_http_dept(self, access_token, dept_id):
        '''
        删除钉钉部门
        '''
        url = DELETE_DEPT_URL.format(access_token)
        params = {
            'dept_id': dept_id
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        request_id = response.get('request_id', "")
        return request_id

    def create_http_user(self, access_token, name, mobile, dept_id_list):
        '''
        创建用户
        '''
        url = CREATE_USER_URL.format(access_token)
        params = {
            'name': name,
            'mobile': mobile,
            'dept_id_list': ",".join([str(x) for x in dept_id_list]),
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        return result
    
    def get_http_by_mobile_user(self, access_token, mobile):
        '''
        根据手机号查询用户ID
        '''
        url = USER_MOBILE_URL.format(access_token)
        params = {
            'mobile': mobile,
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            # raise Exception({'errmsg': errmsg,'errcode': errcode})
            return None
        result = response.get('result', {})
        return result

    def update_http_user_dept(self, access_token, userid, dept_id_list):
        '''
        修改用户部门
        '''
        url = UPDATE_USER_URL.format(access_token)
        params = {
            'userid': userid,
            'dept_id_list': ",".join([str(x) for x in dept_id_list]),
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        return result
    
    def get_http_user(self, access_token, userid):
        '''
        根据用户id获取用户信息
        '''
        url = GET_USER_URL.format(access_token)
        params = {
            'userid': userid,
        }
        response = requests.post(url, json=params).json()
        errmsg = response.get("errmsg", "ok")
        errcode = response.get("errcode", "0")
        if errmsg != "ok":
            raise Exception({'errmsg': errmsg,'errcode': errcode})
        result = response.get('result', {})
        return result

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
    
    def group_recursive_create(self, group, access_token, parent_dept_id, is_first=True):
        '''
        递归分组创建
        '''
        if is_first:
            # 默认为根节点(不能不从根节点走)
            parent_dept_id = int(1)
        # 获取指定部门的子部门
        child_depts = self.get_http_depts(access_token, parent_dept_id)
        child_dept_name_dict = {}
        for child_dept in child_depts:
            child_dept_name = child_dept.get('name', '')
            if child_dept_name:
                child_dept_name_dict[child_dept_name] = child_dept
        if is_first:
            # 对于首项要单独处理创建
            name = group.get('name', '')
            origin_id = 'arkid:{}'.format(group.get('id', ''))
            if name not in child_dept_name_dict:
                dept_id = self.create_http_dept(access_token, name, parent_dept_id, origin_id)
            else:
                dept_id = child_dept_name_dict.get(name).get('dept_id', -1)
            parent_dept_id = dept_id
            group['real_id'] = dept_id
            # 重新计算
            child_depts = self.get_http_depts(access_token, parent_dept_id)
            child_dept_name_dict = {}
            for child_dept in child_depts:
                child_dept_name = child_dept.get('name', '')
                if child_dept_name:
                    child_dept_name_dict[child_dept_name] = child_dept
        # 更新子部门
        for group_child in group.get('children',[]):
            # 新建部门
            name = group_child.get('name', '')
            origin_id = group_child.get('id', '')
            origin_id = 'arkid:{}'.format(origin_id)
            if name not in child_dept_name_dict:
                # 如果没在已有的部门
                dept_id = self.create_http_dept(access_token, name, parent_dept_id, origin_id)
            else:
                # 如果在已有的部门
                dept_id = child_dept_name_dict.get(name).get('dept_id', -1)
                # 需要给已有的部门写上标记
                self.edit_http_dept(access_token, dept_id, origin_id)
            group_child['real_id'] = dept_id
            # 继续遍历子部门
            self.group_recursive_create(group_child, access_token, dept_id, False)

    def get_recursive_depts(self, access_token, items, dept):
        '''
        获取所有部门(递归)
        '''
        dept_id = dept.get('dept_id', 1)
        if dept not in items:
            items.append(dept)

        dept_list = self.get_http_depts(access_token, dept_id)
        for dept in dept_list:
            self.get_recursive_depts(access_token, items, dept)
    
    def get_recursive_users(self, access_token, items, dept_id, cursor):
        '''
        获取用户(递归)
        '''
        has_more, next_cursor, result_list = self.get_http_users(access_token, dept_id, 100, cursor)
        items.extend(result_list)
        if has_more is True:
            self.get_recursive_users(access_token, items, dept_id, next_cursor)
    
    def get_users(self, config):
        '''
        获取用户
        '''
        dept_list = []
        user_list = []
        access_token = self.get_http_access_token(config)
        # 需要先获取公司基础信息
        base_dept = self.get_http_dept(access_token, 1)
        base_dept_obj = {
            'dept_id': base_dept.get('dept_id', 1),
            'name': base_dept.get('name', '')
        }
        # 获取所有部门
        self.get_recursive_depts(access_token, dept_list, base_dept_obj)
        # 获取所有用户
        for dept in dept_list:
            dept_id = dept.get('dept_id', 1)
            self.get_recursive_users(access_token, user_list, dept_id, 0)
        return user_list, dept_list
    
    def get_group(self, config):
        '''
        获取分组
        '''
        dept_list = []
        access_token = self.get_http_access_token(config)
        # 需要先获取公司基础信息
        base_dept = self.get_http_dept(access_token, 1)
        base_dept_obj = {
            'dept_id': base_dept.get('dept_id', 1),
            'name': base_dept.get('name', '')
        }
        # 获取所有部门
        self.get_recursive_depts(access_token, dept_list, base_dept_obj)
        dept_dict = {}
        for dept_item in dept_list:
            dept_item['children'] = []
            dept_dict[dept_item.get('dept_id', 1)] = dept_item

        for dept_item in dept_list:
            parent_id = dept_item.get('parent_id', -1)
            if parent_id != -1:
                dept_obj = dept_dict.get(parent_id)
                children = dept_obj.get('children', [])
                children.append(str(dept_item.get('dept_id', "1")))
                dept_obj['children'] = children
        return dept_list

    def _get_all_scim_users(self, config):
        scim_users = []
        # 获取所有用户开始
        dingding_users, dept_list = self.get_users(config)
        temp_dingding_users = []
        if dingding_users:
            for dingding_user in dingding_users:
                temp_user = {
                    'dept_id_list': dingding_user.get('dept_id_list', []),
                    'active': dingding_user.get('active', ''),
                    'email': dingding_user.get('org_email', ''),
                    'name': dingding_user.get('name', ''),
                    'mobile': dingding_user.get('mobile', ''),
                    'username': dingding_user.get('mobile', ''),
                    'userid': dingding_user.get('userid', '')
                }
                if temp_user not in temp_dingding_users:
                    temp_dingding_users.append(temp_user)
        dingding_users = temp_dingding_users
        # 部门转换为dict
        dept_dict = {}
        for dept_item in dept_list:
            dept_item_id = dept_item.get('dept_id', 1)
            dept_dict[dept_item_id] = dept_item
        # 获取所有用户结束
        for dingding_user in dingding_users:
            dept_id_list = dingding_user.get('dept_id_list', [])
            depts = []
            for dept_id in dept_id_list:
                dept = dept_dict.get(dept_id, None)
                if dept:
                    dept_name = dept.get('name', '')
                    depts.append({
                        'id': dept_id,
                        'name': dept_name,
                    })
            dingding_user['depts'] = depts
            scim_user = self._get_scim_user(dingding_user)
            scim_users.append(scim_user)
        return scim_users

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


extension = ScimSyncDingDingExtension()
