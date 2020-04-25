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

    def __init__(self, authorizer=None, **kwargs):
        BaseClient.__init__(self, "node", authorizer=authorizer, **kwargs)

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
        return self.delete(path='{}/'.format(node_uid))

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

    def update_subnode(self, node_uid: str, json_body: dict):
        """
        编辑指定节点的子节点的信息
        :param node_uid: 节点的唯一标识
        :param json_body: 节点的元信息, 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.update_subnode() 接口与 ArkID 服务端进行交互")
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

    def update_user_under_node(self, node_uid: str, json_body: dict, **params):
        """
        更新指定节点下的指定直属人员的信息
        :param node_uid: 节点的唯一标识
        :param json_body: 用户的元信息，参数详情请参考接口文档
        :param params: 用户的元信息，参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 NodeClient.update_user_under_node() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body, params=params)
