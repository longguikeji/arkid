"""
Define ArkIDClient
"""
from arkid_client.base import BaseClient, reload_service
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.authorizers import NullAuthorizer
from arkid_client.exceptions import ArkIDError

from arkid_client import (UserClient, OrgClient, NodeClient)


class ArkIDClient(BaseClient):
    """
    由各种 ArkID 客户端集成而生，他提供的所有功能
    都只是各个客户端的简单封装，用来一致对外界用户
    使用;
    默认加载的为 user 相关服务接口
    当然，如果您足够熟悉本项目，您也可以直接实例化
    您所需要的指定客户端。
    """
    allowed_authorizer_types = [
        BasicAuthorizer,
        NullAuthorizer,
    ]

    def __init__(self, base_url, authorizer=None, *args, **kwargs):
        self.__user_client = None
        self.__org_client = None
        self.__node_client = None
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
    def query_user(self,
                   keyword: str = None,
                   wechat_unionid: str = None,
                   page: int = 1,
                   page_size: int = 30):
        """
        调用底层 < UserClient > 实例的 query_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_user(keyword=keyword,
                                             wechat_unionid=wechat_unionid,
                                             page=page,
                                             page_size=page_size)

    @reload_service('user')
    def query_isolated_user(self,
                            page: int = 1,
                            page_size: int = 30):
        """
        调用底层 < UserClient > 实例的 query_isolated_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_isolated_user(page=page, page_size=page_size)

    @reload_service('user')
    def query_specified_user(self, username: str):
        """
        调用底层 < UserClient > 实例的 query_specified_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_specified_user(username)

    @reload_service('user')
    def create_user(self, json_body: dict):
        """
        调用底层 < UserClient > 实例的 create_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.create_user(json_body)

    @reload_service('user')
    def update_specified_user(self, username: str, json_body: dict):
        """
        调用底层 < UserClient > 实例的 update_specified_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.update_specified_user(username, json_body)

    @reload_service('user')
    def delete_specified_user(self, username: str):
        """
        调用底层 < UserClient > 实例的 delete_specified_user 方法
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.delete_specified_user(username)

    @reload_service('org')
    def query_own_org(self,
                      page: int = 1,
                      page_size: int = 30):
        """
        调用底层 < OrgClient > 实例的 query_own_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_own_org(page=page, page_size=page_size)

    @reload_service('org')
    def query_specified_org(self, oid: str):
        """
        调用底层 < OrgClient > 实例的 query_specified_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_specified_org(oid)

    @reload_service('org')
    def create_org(self, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 create_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.create_org(json_body)

    @reload_service('org')
    def delete_specified_org(self, oid: str):
        """
        调用底层 < OrgClient > 实例的 delete_specified_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.delete_specified_org(oid)

    @reload_service('org')
    def update_specified_org(self, oid: str, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 update_specified_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.update_specified_org(oid, json_body)

    @reload_service('org')
    def query_orguser(self,
                      oid: str,
                      page: int = 1,
                      page_size: int = 30):
        """
        调用底层 < OrgClient > 实例的 query_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_orguser(oid, page=page, page_size=page_size)

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
    def query_specified_orguser(self, oid: str, username: str):
        """
        调用底层 < OrgClient > 实例的 query_specified_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.query_specified_orguser(oid, username)

    @reload_service('org')
    def update_specified_orguser(self, oid: str, username: str, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 update_specified_orguser 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.update_specified_orguser(oid, username, json_body)

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

    @reload_service('org')
    def get_current_org(self):
        """
        调用底层 < OrgClient > 实例的 get_current_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.get_current_org()

    @reload_service('org')
    def switch_current_org(self, json_body: dict):
        """
        调用底层 < OrgClient > 实例的 switch_current_org 方法
        """
        self.__org_client = self.__init_client(OrgClient)
        return self.__org_client.switch_current_org(json_body)

    @reload_service('node')
    def query_specified_node(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 query_specified_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.query_specified_node(node_uid)

    @reload_service('node')
    def view_specified_node(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 view_specified_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.view_specified_node(node_uid)

    @reload_service('node')
    def update_specified_node(self, node_uid: str, json_body: dict):
        """
        调用底层 < NodeClient > 实例的 update_specified_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.update_specified_node(node_uid, json_body)

    @reload_service('node')
    def delete_specified_node(self,
                              node_uid: str,
                              ignore_user: bool = True):
        """
        调用底层 < NodeClient > 实例的 delete_specified_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.delete_specified_node(node_uid, ignore_user=ignore_user)

    @reload_service('node')
    def get_node_tree_list(self, node_uid: str):
        """
        调用底层 < NodeClient > 实例的 get_node_tree_list 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.get_node_tree_list(node_uid)

    @reload_service('node')
    def get_node_tree(self,
                      node_uid: str,
                      user_required: bool = False):
        """
        调用底层 < NodeClient > 实例的 get_node_tree 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.get_node_tree(node_uid, user_required=user_required)

    @reload_service('node')
    def view_node_tree(self,
                       node_uid: str,
                       user_required: bool = False):
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
    def query_user_under_node(self, node_uid: str, name: str = None,
                              username: str = None, mobile: str = None, email: str = None,
                              before_created: str = None, after_created: str = None,
                              before_last_active_time: str = None, after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 query_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.query_user_under_node(node_uid, name=name,
                                                        username=username, mobile=mobile, email=email,
                                                        before_created=before_created, after_created=after_created,
                                                        before_last_active_time=before_last_active_time,
                                                        after_last_active_time=after_last_active_time)

    @reload_service('node')
    def add_user_under_node(self, node_uid: str, user_uids: list, name: str = None,
                            username: str = None, mobile: str = None, email: str = None,
                            before_created: str = None, after_created: str = None,
                            before_last_active_time: str = None, after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 add_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.add_user_under_node(node_uid, user_uids, name=name,
                                                      username=username, mobile=mobile, email=email,
                                                      before_created=before_created, after_created=after_created,
                                                      before_last_active_time=before_last_active_time,
                                                      after_last_active_time=after_last_active_time)

    @reload_service('node')
    def delete_user_under_node(self, node_uid: str, user_uids: list, name: str = None,
                               username: str = None, mobile: str = None, email: str = None,
                               before_created: str = None, after_created: str = None,
                               before_last_active_time: str = None, after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 delete_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.delete_user_under_node(node_uid, user_uids, name=name,
                                                         username=username, mobile=mobile, email=email,
                                                         before_created=before_created, after_created=after_created,
                                                         before_last_active_time=before_last_active_time,
                                                         after_last_active_time=after_last_active_time)

    @reload_service('node')
    def sort_user_under_node(self, node_uid: str, user_uids: list, name: str = None,
                             username: str = None, mobile: str = None, email: str = None,
                             before_created: str = None, after_created: str = None,
                             before_last_active_time: str = None, after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 sort_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.sort_user_under_node(node_uid, user_uids, name=name,
                                                       username=username, mobile=mobile, email=email,
                                                       before_created=before_created, after_created=after_created,
                                                       before_last_active_time=before_last_active_time,
                                                       after_last_active_time=after_last_active_time)

    @reload_service('node')
    def override_user_under_node(self, node_uid: str, user_uids: list, name: str = None,
                                 username: str = None, mobile: str = None, email: str = None,
                                 before_created: str = None, after_created: str = None,
                                 before_last_active_time: str = None, after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 override_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.override_user_under_node(node_uid, user_uids, name=name,
                                                           username=username, mobile=mobile, email=email,
                                                           before_created=before_created, after_created=after_created,
                                                           before_last_active_time=before_last_active_time,
                                                           after_last_active_time=after_last_active_time)

    @reload_service('node')
    def move_out_user_under_node(self, node_uid: str, user_uids: list, name: str = None,
                                 username: str = None, mobile: str = None, email: str = None,
                                 before_created: str = None, after_created: str = None,
                                 before_last_active_time: str = None, after_last_active_time: str = None):
        """
        调用底层 < NodeClient > 实例的 move_out_user_under_node 方法
        """
        self.__node_client = self.__init_client(NodeClient)
        return self.__node_client.move_out_user_under_node(node_uid, user_uids, name=name,
                                                           username=username, mobile=mobile, email=email,
                                                           before_created=before_created, after_created=after_created,
                                                           before_last_active_time=before_last_active_time,
                                                           after_last_active_time=after_last_active_time)
