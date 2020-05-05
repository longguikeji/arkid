"""
Define ArkIDClient
"""
from arkid_client.base import BaseClient, reload_service
from arkid_client.authorizers import BasicAuthorizer, NullAuthorizer
from arkid_client.exceptions import ArkIDError
from arkid_client import (
    UserClient,
    OrgClient,
    NodeClient,
    UcenterClient,
    PermClient,
    AppClient,
    InfrastructureClient
)


class ArkIDClient(BaseClient):
    """
    由各种 ArkID 客户端集成而生，
    他提供的所有功能都只是各个客户端的简单封装，
    用来一致对外界用户使用;默认加载的为 user 相关服务接口
    当然，如果您足够熟悉本项目，
    您也可以直接实例化所需要的指定客户端。

    **Methods**

    *  :py:meth:`.query_user`
    *  :py:meth:`.query_isolated_user`
    *  :py:meth:`.query_user`
    *  :py:meth:`.create_user`
    *  :py:meth:`.update_user`
    *  :py:meth:`.delete_user`
    *  :py:meth:`.query_specified_perm`
    *  :py:meth:`.query_own_org`
    *  :py:meth:`.query_org`
    *  :py:meth:`.create_org`
    *  :py:meth:`.delete_org`
    *  :py:meth:`.update_org`
    *  :py:meth:`.query_orguser`
    *  :py:meth:`.add_orguser`
    *  :py:meth:`.delete_orguser`
    *  :py:meth:`.query_orguser`
    *  :py:meth:`.update_orguser`
    *  :py:meth:`.get_org_invitation_key`
    *  :py:meth:`.refresh_org_invitation_key`
    *  :py:meth:`.view_org_by_invitation_key`
    *  :py:meth:`.join_org_by_invitation_key`
    *  :py:meth:`.query_node`
    *  :py:meth:`.view_node`
    *  :py:meth:`.update_node`
    *  :py:meth:`.delete_node`
    *  :py:meth:`.get_node_tree_list`
    *  :py:meth:`.get_node_tree`
    *  :py:meth:`.view_node_tree`
    *  :py:meth:`.get_subnode`
    *  :py:meth:`.create_subnode`
    *  :py:meth:`.add_subnode`
    *  :py:meth:`.sort_subnode`
    *  :py:meth:`.query_user_under_node`
    *  :py:meth:`.add_user_under_node`
    *  :py:meth:`.delete_user_under_node`
    *  :py:meth:`.override_user_under_node`
    *  :py:meth:`.sort_user_under_node`
    *  :py:meth:`.move_out_user_under_node`
    *  :py:meth:`.view_perm`
    *  :py:meth:`.view_profile`
    *  :py:meth:`.view_current_org`
    *  :py:meth:`.switch_current_org`
    *  :py:meth:`.query_apps`
    *  :py:meth:`.get_sms_captcha`
    *  :py:meth:`.verify_sms_captcha`
    *  :py:meth:`.query_all_perm`
    *  :py:meth:`.create_perm`
    *  :py:meth:`.query_perm`
    *  :py:meth:`.update_perm`
    *  :py:meth:`.query_perm_owner`
    *  :py:meth:`.update_perm_owner`
    *  :py:meth:`.query_specified_user_perm`
    *  :py:meth:`.update_specified_user_perm`
    *  :py:meth:`.query_dept_perm`
    *  :py:meth:`.update_dept_perm`
    *  :py:meth:`.query_group_perm`
    *  :py:meth:`.update_group_perm`
    *  :py:meth:`.query_node_perm`
    *  :py:meth:`.update_node_perm`
    *  :py:meth:`.query_app_list`
    *  :py:meth:`.create_app`
    *  :py:meth:`.query_app`
    *  :py:meth:`.update_app`
    *  :py:meth:`.delete_app`
    *  :py:meth:`.register_app`
    """
    allowed_authorizer_types = [
        BasicAuthorizer,
        NullAuthorizer,
    ]

    def __init__(self, base_url, authorizer=None, *args, **kwargs):
        self.__user_client = None
        self.__org_client = None
        self.__node_client = None
        self.__ucenter_client = None
        self.__perm_client = None
        self.__app_client = None
        self.__infrastructure_client = None
        BaseClient.__init__(self, base_url, 'user', authorizer=authorizer, *args, **kwargs)

    def __init_client(self, client_class):
        """
        规范所有子客户端集成到 < ArkIDClient > 。由于 < ArkIDClient >
        是由各子客户端组合而成，本身并不提供任何功能。所以，最好将子客户
        端集成的操作流程化。
        """
        classname = client_class.__name__.lower().replace('client', '')
        attr = '_ArkIDClient__{}_client'.format(classname)
        if not hasattr(self, attr):
            raise ArkIDError('无法初始化暂不支持的客户端类型')
        _client = getattr(self, attr)
        if not _client:
            _client = client_class(authorizer=self.authorizer, base_url=self.base_url)
            setattr(self, attr, _client)
        return _client

    @reload_service('user')
    def query_user_list(self, keyword: str = None, wechat_unionid: str = None, page: int = 1, page_size: int = 30):
        """
        调用底层 < UserClient > 实例的 query_user_list 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_user_list(keyword=keyword,
                                                  wechat_unionid=wechat_unionid,
                                                  page=page,
                                                  page_size=page_size)

    @reload_service('user')
    def query_isolated_user(self, page: int = 1, page_size: int = 30):
        """
        调用底层 < UserClient > 实例的 query_isolated_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_isolated_user(page=page, page_size=page_size)

    @reload_service('user')
    def query_user(self, username: str):
        """
        调用底层 < UserClient > 实例的 query_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_user(username)

    @reload_service('user')
    def create_user(self, json_body: dict):
        """
        调用底层 < UserClient > 实例的 create_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.create_user(json_body)

    @reload_service('user')
    def update_user(self, username: str, json_body: dict):
        """
        调用底层 < UserClient > 实例的 update_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.update_user(username, json_body)

    @reload_service('user')
    def delete_user(self, username: str):
        """
        调用底层 < UserClient > 实例的 delete_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.delete_user(username)

    @reload_service('user')
    def query_specified_perm(self, username: str, uid: str):
        """
        调用底层 < UserClient > 实例的 query_specified_perm 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_specified_perm(username, uid)

    @reload_service('org')
    def query_own_org(self, page: int = 1, page_size: int = 30):
        """
        调用底层 < OrgClient > 实例的 query_own_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_own_org(page=page, page_size=page_size)

    @reload_service('org')
    def query_org(self, oid: str):
        """
        调用底层 < OrgClient > 实例的 query_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_org(oid)

    @reload_service('org')
    def create_org(self, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 create_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.create_org(json_body)

    @reload_service('org')
    def delete_org(self, oid: str):
        """
        调用底层 < OrgClient > 实例的 delete_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.delete_org(oid)

    @reload_service('org')
    def update_org(self, oid: str, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 update_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.update_org(oid, json_body)

    @reload_service('org')
    def query_orguser_list(self, oid: str, page: int = 1, page_size: int = 30):
        """
        调用底层 < OrgClient > 实例的 query_orguser_list 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_orguser_list(oid, page=page, page_size=page_size)

    @reload_service('org')
    def add_orguser(self, oid: str, usernames: list):
        """
        调用底层 < OrgClient > 实例的 add_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.add_orguser(oid, usernames)

    @reload_service('org')
    def delete_orguser(self, oid: str, usernames: list):
        """
        调用底层 < OrgClient > 实例的 delete_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.delete_orguser(oid, usernames)

    @reload_service('org')
    def query_orguser(self, oid: str, username: str):
        """
        调用底层 < OrgClient > 实例的 query_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_orguser(oid, username)

    @reload_service('org')
    def update_orguser(self, oid: str, username: str, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 update_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.update_orguser(oid, username, json_body)

    @reload_service('org')
    def get_org_invitation_key(self, oid: str):
        """
        调用底层 < OrgClient > 实例的 get_org_invitation_key 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.get_org_invitation_key(oid)

    @reload_service('org')
    def refresh_org_invitation_key(self, oid: str):
        """
        调用底层 < OrgClient > 实例的 refresh_org_invitation_key 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.refresh_org_invitation_key(oid)

    @reload_service('org')
    def view_org_by_invitation_key(self, oid: str, invite_link_key: str):
        """
        调用底层 < OrgClient > 实例的 view_org_by_invitation_key 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.view_org_by_invitation_key(oid, invite_link_key)

    @reload_service('org')
    def join_org_by_invitation_key(self, oid: str, invite_link_key: str):
        """
        调用底层 < OrgClient > 实例的 join_org_by_invitation_key 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.join_org_by_invitation_key(oid, invite_link_key)

    @reload_service('node')
    def query_node(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 query_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.query_node(node_uid)

    @reload_service('node')
    def view_node(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 view_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.view_node(node_uid)

    @reload_service('node')
    def update_node(self, node_uid: str, json_body: dict):
        """
        调用底层 < NodeClient > 实例的 update_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.update_node(node_uid, json_body)

    @reload_service('node')
    def delete_node(self, node_uid: str, ignore_user: bool = True):
        """
        调用底层 < NodeClient > 实例的 delete_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.delete_node(node_uid, ignore_user=ignore_user)

    @reload_service('node')
    def get_node_tree_list(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 get_node_tree_list 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.get_node_tree_list(node_uid)

    @reload_service('node')
    def get_node_tree(self, node_uid: str, user_required: bool = False):
        """
        调用底层 < NodeClient > 实例的 get_node_tree 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.get_node_tree(node_uid, user_required=user_required)

    @reload_service('node')
    def view_node_tree(self, node_uid: str, user_required: bool = False):
        """
        调用底层 < NodeClient > 实例的 view_node_tree 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.view_node_tree(node_uid, user_required=user_required)

    @reload_service('node')
    def get_subnode(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 get_subnode 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.get_subnode(node_uid)

    @reload_service('node')
    def create_subnode(self, node_uid: str, json_body: dict):
        """
        调用底层 < NodeClient > 实例的 create_subnode 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.create_subnode(node_uid, json_body)

    @reload_service('node')
    def add_subnode(self, node_uid: str, node_uids: list):
        """
        调用底层 < NodeClient > 实例的 add_subnode 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.add_subnode(node_uid, node_uids)

    @reload_service('node')
    def sort_subnode(self, node_uid: str, node_uids: list):
        """
        调用底层 < NodeClient > 实例的 sort_subnode 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.sort_subnode(node_uid, node_uids)

    @reload_service('node')
    def query_user_under_node(self,
                              node_uid: str,
                              name: str = None,
                              username: str = None,
                              mobile: str = None,
                              email: str = None,
                              before_created: str = None,
                              after_created: str = None,
                              before_last_active_time: str = None,
                              after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 query_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.query_user_under_node(node_uid,
                                                        name=name,
                                                        username=username,
                                                        mobile=mobile,
                                                        email=email,
                                                        before_created=before_created,
                                                        after_created=after_created,
                                                        before_last_active_time=before_last_active_time,
                                                        after_last_active_time=after_last_active_time)

    @reload_service('node')
    def add_user_under_node(self, node_uid: str, user_uids: list):
        """
        调用底层 < NodeClient > 实例的 add_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.add_user_under_node(node_uid, user_uids)

    @reload_service('node')
    def delete_user_under_node(self, node_uid: str, user_uids: list):
        """
        调用底层 < NodeClient > 实例的 delete_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.delete_user_under_node(node_uid, user_uids)

    @reload_service('node')
    def sort_user_under_node(self, node_uid: str, user_uids: list):
        """
        调用底层 < NodeClient > 实例的 sort_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.sort_user_under_node(node_uid, user_uids)

    @reload_service('node')
    def override_user_under_node(self, node_uid: str, user_uids: list):
        """
        调用底层 < NodeClient > 实例的 override_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.override_user_under_node(node_uid, user_uids)

    @reload_service('node')
    def move_out_user_under_node(self, node_uid: str, user_uids: list):
        """
        调用底层 < NodeClient > 实例的 move_out_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.move_out_user_under_node(node_uid, user_uids)

    @reload_service('ucenter')
    def view_perm(self):
        """
        调用底层 < UcenterClient > 实例的 view_perm 方法
        """
        self.__ucenter_client = self.__init_client(UcenterClient)
        return self.__ucenter_client.view_perm()

    @reload_service('ucenter')
    def view_profile(self):
        """
        调用底层 < UcenterClient > 实例的 view_profile 方法
        """
        self.__ucenter_client = self.__init_client(UcenterClient)
        return self.__ucenter_client.view_profile()

    @reload_service('ucenter')
    def view_current_org(self):
        """
        调用底层 < UcenterClient > 实例的 view_current_org 方法
        """
        self.__ucenter_client = self.__init_client(UcenterClient)
        return self.__ucenter_client.view_current_org()

    @reload_service('ucenter')
    def switch_current_org(self, json_body: dict):
        """
        调用底层 < UcenterClient > 实例的 switch_current_org 方法
        """
        self.__ucenter_client = self.__init_client(UcenterClient)
        return self.__ucenter_client.switch_current_org(json_body)

    @reload_service('ucenter')
    def query_apps(self, name: str = None):
        """
        调用底层 < UcenterClient > 实例的 ucenter 方法
        """
        self.__ucenter_client = self.__init_client(UcenterClient)
        return self.__ucenter_client.query_apps(name=name)

    @reload_service('infrastructure')
    def get_sms_captcha(self, action: str, mobile: str, **kwargs):
        """
        调用底层 < InfrastructureClient > 实例的 get_current_org 方法
        """
        self.__infrastructure_client = self.__init_client(InfrastructureClient)
        return self.__infrastructure_client.get_sms_captcha(action, mobile, **kwargs)

    @reload_service('infrastructure')
    def verify_sms_captcha(self, action: str, mobile: str, code: str):
        """
        调用底层 < InfrastructureClient > 实例的 verify_sms_captcha 方法
        """
        self.__infrastructure_client = self.__init_client(InfrastructureClient)
        return self.__infrastructure_client.verify_sms_captcha(action, mobile, code)

    @reload_service('perm')
    def query_all_perm(self):
        """
        调用底层 < PermClient > 实例的 query_all_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_all_perm()

    @reload_service('perm')
    def create_perm(self, json_body: dict):
        """
        调用底层 < PermClient > 实例的 create_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.create_perm(json_body)

    @reload_service('perm')
    def query_perm(self, uid: str):
        """
        调用底层 < PermClient > 实例的 query_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_perm(uid)

    @reload_service('perm')
    def update_perm(self, uid: str, json_body: dict):
        """
        调用底层 < PermClient > 实例的 update_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.update_perm(uid, json_body)

    @reload_service('perm')
    def query_perm_owner(self, uid: str,
                         owner_subject: str = None,
                         value: bool = True,
                         status: int = 1):
        """
        调用底层 < PermClient > 实例的 query_perm_owner 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_perm_owner(uid,
                                                   owner_subject=owner_subject,
                                                   value=value,
                                                   status=status)

    @reload_service('perm')
    def update_perm_owner(self, uid: str,
                          owner_subject: str = None,
                          value: bool = True,
                          status: int = 1):
        """
        调用底层 < PermClient > 实例的 update_perm_owner 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.update_perm_owner(uid,
                                                    owner_subject=owner_subject,
                                                    value=value,
                                                    status=status)

    @reload_service('perm')
    def query_specified_user_perm(self,
                                  username: str,
                                  action: str = None,
                                  action_except: str = None,
                                  scope: str = None):
        """
        调用底层 < PermClient > 实例的 query_user_all_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_specified_user_perm(username,
                                                            action=action,
                                                            action_except=action_except,
                                                            scope=scope)

    @reload_service('perm')
    def update_specified_user_perm(self,
                                   username: str,
                                   json_body: dict):
        """
        调用底层 < PermClient > 实例的 update_specified_user_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.update_specified_user_perm(username, json_body)

    @reload_service('perm')
    def query_dept_perm(self,
                        uid: str,
                        action: str = None,
                        action_except: str = None,
                        scope: str = None):
        """
        调用底层 < PermClient > 实例的 query_dept_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_dept_perm(uid,
                                                  action=action,
                                                  action_except=action_except,
                                                  scope=scope)

    @reload_service('perm')
    def update_dept_perm(self,
                         uid: str,
                         json_body: dict):
        """
        调用底层 < PermClient > 实例的 update_dept_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.update_dept_perm(uid, json_body)

    @reload_service('perm')
    def query_group_perm(self,
                         uid: str,
                         action: str = None,
                         action_except: str = None,
                         scope: str = None):
        """
        调用底层 < PermClient > 实例的 query_group_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_group_perm(uid,
                                                   action=action,
                                                   action_except=action_except,
                                                   scope=scope)

    @reload_service('perm')
    def update_group_perm(self, uid: str, json_body: dict):
        """
        调用底层 < PermClient > 实例的 update_group_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.update_group_perm(uid, json_body)

    @reload_service('perm')
    def query_node_perm(self,
                        node_uid: str,
                        action: str = None,
                        action_except: str = None,
                        scope: str = None):
        """
        调用底层 < PermClient > 实例的 query_node_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.query_node_perm(node_uid,
                                                  action=action,
                                                  action_except=action_except,
                                                  scope=action_except)

    @reload_service('perm')
    def update_node_perm(self, node_uid: str, json_body: dict):
        """
        调用底层 < PermClient > 实例的 update_node_perm 方法
        """
        self.__perm_client = self.__init_client(PermClient)
        return self.__perm_client.update_node_perm(node_uid, json_body)

    @reload_service('app')
    def query_app_list(self,
                       oid: str = None,
                       name: str = None,
                       node_uid: str = None,
                       user_uid: str = None,
                       owner_access: bool = False):
        """
        调用底层 < AppClient > 实例的 query_app_list 方法
        """
        self.__app_client = self.__init_client(AppClient)
        return self.__app_client.query_app_list(oid, name=name,
                                                node_uid=node_uid,
                                                user_uid=user_uid,
                                                owner_access=owner_access)

    @reload_service('app')
    def create_app(self, oid: str, json_body: dict):
        """
        调用底层 < AppClient > 实例的 create_app 方法
        """
        self.__app_client = self.__init_client(AppClient)
        return self.__app_client.create_app(oid, json_body)

    @reload_service('app')
    def query_app(self, oid: str, uid: str):
        """
        调用底层 < AppClient > 实例的 query_app 方法
        """
        self.__app_client = self.__init_client(AppClient)
        return self.__app_client.query_app(oid, uid)

    @reload_service('app')
    def update_app(self, oid: str, uid: str, json_body: dict):
        """
        调用底层 < AppClient > 实例的 update_app 方法
        """
        self.__app_client = self.__init_client(AppClient)
        return self.__app_client.update_app(oid, uid, json_body)

    @reload_service('app')
    def delete_app(self, oid: str, uid: str):
        """
        调用底层 < AppClient > 实例的 delete_app 方法
        """
        self.__app_client = self.__init_client(AppClient)
        return self.__app_client.delete_app(oid, uid)

    @reload_service('app')
    def register_app(self, oid: str, uid: str, protocol: str, json_body: dict):
        """
        调用底层 < AppClient > 实例的 register_app 方法
        """
        self.__app_client = self.__init_client(AppClient)
        return self.__app_client.register_app(oid, uid, protocol, json_body)
