"""
Define NodeClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient, reload_service
from arkid_client.exceptions import NodeAPIError
from arkid_client.response import ArkIDHTTPResponse


class NodeClient(BaseClient):
    """
    节点管理客户端，用于与 ArkID 服务端节点管理相关
    接口的访问操作。
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = NodeAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "node", authorizer=authorizer, **kwargs)

    def query_specified_node(self, node_uid: str):
        """
        查询指定节点的信息
        :param node_uid: 节点的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.query_specified_node() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(node_uid))

    @reload_service('ucenter')
    def view_specified_node(self, node_uid: str):
        """
        用户查询指定节点的信息
        :param node_uid: 节点的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.view_specified_node() 接口与 ArkID 服务端进行交互")
        return self.get(path='node/{}/'.format(node_uid))

    def update_specified_node(self, node_uid: str, json_body: dict):
        """
        修改指定节点的信息

        :param node_uid: 节点的唯一标识
        :param json_body: 节点的元信息, 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.update_specified_node() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(node_uid), json_body=json_body)

    def delete_specified_node(self, node_uid: str, **params):
        """
        删除指定节点的信息
        :param node_uid: 节点的唯一标识
        :param params:

            ``ignore_user`` (*bool*)
              用于删除节点，当true时，若节点下有人员存在时，
              会先将人员从节点内删除，再删除此节点。

        :return: :class: < ArkIDHTTPResponse > object
        """
        return self.delete(path='{}/'.format(node_uid), params=params)

    def get_node_tree_list(self, node_uid: str):
        """
        需要管理员权限，获取节点及其子孙节点列表，将某节点下
        的子树以列表形式返回，包括该节点自身，前序遍历。
        :param node_uid: 节点的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.get_node_tree_list() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/list/'.format(node_uid))

    def get_node_tree(self, node_uid: str, **params):
        """
        需要管理员权限，管理员访问到的数据将由管理范围决定，
        数据包括从该节点起始的完整树。
        :param node_uid: 节点的唯一标识
        :param params:

            ``user_required`` (*bool*)
              是否需要成员信息

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.get_node_tree() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/tree/'.format(node_uid), params=params)

    @reload_service('ucenter')
    def view_node_tree(self, node_uid: str, **params):
        """
        普通用户访问节点下结构，访问到的数据将由节点可见范围
        决定，数据包括从该节点起始的完整树。
        :param node_uid: 节点的唯一标识
        :param params:

            ``user_required`` (*bool*)
              是否需要成员信息

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.view_node_tree() 接口与 ArkID 服务端进行交互")
        return self.get(path='node/{}/tree/'.format(node_uid), params=params)

    def get_subnode(self, node_uid: str):
        """
        获取指定节点的子节点信息
        :param node_uid: 节点的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.get_node_tree() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/node/'.format(node_uid))

    def create_subnode(self, node_uid: str, json_body: dict):
        """
        创建指定节点的子节点
        :param node_uid: 节点的唯一标识
        :param json_body: 节点的元信息, 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.create_subnode() 接口与 ArkID 服务端进行交互")
        return self.post(path='{}/node/'.format(node_uid), json_body=json_body)

    def add_subnode(self, node_uid: str, node_uids: list):
        """
        向指定节点添加子节点
        :param node_uid: 节点的唯一标识
        :param node_uids: 节点唯一标识组成的列表
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.add_subnode() 接口与 ArkID 服务端进行交互")
        json_body = {'subject': 'add', 'node_uids': node_uids}
        return self.patch(path='{}/node/'.format(node_uid), json_body=json_body)

    def sort_subnode(self, node_uid: str, node_uids: list):
        """
        对指定子节点按指定位置进行排序
        :param node_uid: 节点的唯一标识
        :param node_uids: 节点唯一标识组成的列表
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.sort_subnode() 接口与 ArkID 服务端进行交互")
        json_body = {'subject': 'sort', 'node_uids': node_uids}
        return self.patch(path='{}/node/'.format(node_uid), json_body=json_body)

    def query_user_under_node(self, node_uid: str, **params):
        """
        查询指定节点下的直属人员的信息
        :param node_uid: 节点的唯一标识
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.query_user_under_node() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/user/'.format(node_uid), params=params)

    def add_user_under_node(self, node_uid: str, user_uids: list, **params):
        """
        向指定节点添加指定成员
        :param node_uid: 节点的唯一标识
        :param user_uids: 用户唯一标识组成的列表
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.add_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'add'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body, params=params)

    def delete_user_under_node(self, node_uid: str, user_uids: list, **params):
        """
        从指定节点移除指定成员
        :param node_uid: 节点的唯一标识
        :param user_uids: 用户唯一标识组成的列表
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.delete_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'delete'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body, params=params)

    def override_user_under_node(self, node_uid: str, user_uids: list, **params):
        """
        重置指定节点的指定用户
        :param node_uid: 节点的唯一标识
        :param user_uids: 用户唯一标识组成的列表
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.override_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'override'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body, params=params)

    def sort_user_under_node(self, node_uid: str, user_uids: list, **params):
        """
        对指定人按指定位置进行排序
        :param node_uid: 节点的唯一标识
        :param user_uids: 用户唯一标识组成的列表
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.sort_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'sort'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body, params=params)

    def move_out_user_under_node(self, node_uid: str, user_uids: list, **params):
        """
        将这些人从该节点移除，并加到指定节点
        :param node_uid: 节点的唯一标识
        :param user_uids: 用户唯一标识组成的列表
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.move_out_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'move_out'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body, params=params)
