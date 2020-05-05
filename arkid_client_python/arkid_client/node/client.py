"""
Define NodeClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import NodeAPIError
from arkid_client.response import ArkIDHTTPResponse


class NodeClient(BaseClient):
    """
    节点管理客户端，用于与 ArkID 服务端节点管理相关
    接口的访问操作。

    **Methods**

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

    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = NodeAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "node", authorizer=authorizer, **kwargs)

    def query_node(self, node_uid: str):
        """
        查询指定节点的信息
        (``GET /siteapi/v1/node/<node_uid>/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> node = nc.query_node(node_uid)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.query_node() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(node_uid))

    def view_node(self, node_uid: str):
        """
        用户查询指定节点的信息
        (``GET /siteapi/v1/ucenter/node/<node_uid>/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> node = nc.view_node(node_uid)
        >>> print('node is', node)
        """
        _service = self.service
        self.reload_service_url('ucenter')

        self.logger.info("正在调用 NodeClient.view_node() 接口与 ArkID 服务端进行交互")
        response = self.get(path='node/{}/'.format(node_uid))

        self.reload_service_url(_service)
        return response

    def update_node(self, node_uid: str, json_body: dict):
        """
        修改指定节点的信息
        (``PATCH /siteapi/v1/node/<node_uid>/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``json_body`` (*dict*)
              节点的元信息, 参数详情请参考接口文档

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> node_data = {
        >>>     'name': 'example'
        >>> }
        >>> node = nc.update_node(node_uid, node_data)
        >>> print('node is', node)

        **External Documentation**

        关于 `节点的元数据 \
        <https://arkid.docs.apiary.io/#reference/node/0/1>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 NodeClient.update_node() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(node_uid), json_body=json_body)

    def delete_node(self, node_uid: str, **params):
        """
        删除指定节点的信息
        (``DELETE /siteapi/v1/node/<node_uid>/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``ignore_user`` (*bool*)
              用于删除节点，当``true``时，若节点下有人员存在时，
              会先将人员从节点内删除，再删除此节点。

        **Examples**
        self.logger.info("正在调用 NodeClient.delete_node() 接口与 ArkID 服务端进行交互")
        >>> nc = arkid_client.NodeClient(...)
        >>> nc.delete_node(node_uid, ignore_user=True)
        """

        return self.delete(path='{}/'.format(node_uid), params=params)

    def get_node_tree_list(self, node_uid: str):
        """
        需要管理员权限，获取节点及其子孙节点列表，将某节点下
        的子树以列表形式返回，包括该节点自身，前序遍历。
        (``GET /siteapi/v1/node/<node_uid>/list/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> tree_list = nc.get_node_tree_list(node_uid)
        >>> print('tree_list is', tree_list)
        """
        self.logger.info("正在调用 NodeClient.get_node_tree_list() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/list/'.format(node_uid))

    def get_node_tree(self, node_uid: str, **params):
        """
        需要管理员权限，管理员访问到的数据将由管理范围决定，
        数据包括从该节点起始的完整树。
        (``GET /siteapi/v1/node/<node_uid>/tree/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_required`` (*bool*)
              是否需要成员信息

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> tree = nc.get_node_tree(node_uid, user_required=True)
        >>> print('tree is', tree)
        """
        self.logger.info("正在调用 NodeClient.get_node_tree() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/tree/'.format(node_uid), params=params)

    def view_node_tree(self, node_uid: str, **params):
        """
        普通用户访问节点下结构，访问到的数据将由节点可见范围决定，
        数据包括从该节点起始的完整树。
        (``GET /siteapi/v1/ucenter/node/<node_uid>/tree/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_required`` (*bool*)
              是否需要成员信息

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> tree = nc.view_node_tree(node_uid, user_required=True)
        >>> print('tree is', tree)
        """
        _service = self.service
        self.reload_service_url('ucenter')

        self.logger.info("正在调用 NodeClient.view_node_tree() 接口与 ArkID 服务端进行交互")
        response = self.get(path='node/{}/tree/'.format(node_uid), params=params)

        self.reload_service_url(_service)
        return response

    def get_subnode(self, node_uid: str):
        """
        获取指定节点的子节点信息
        (``GET /siteapi/v1/node/<node_uid>/node/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> subnode = nc.get_subnode(node_uid)
        >>> print('subnode is', subnode)
        """
        self.logger.info("正在调用 NodeClient.get_node_tree() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/node/'.format(node_uid))

    def create_subnode(self, node_uid: str, json_body: dict):
        """
        创建指定节点的子节点
        (``POST /siteapi/v1/node/<node_uid>/node/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``json_body`` (*dict*)
              节点的元信息, 参数详情请参考接口文档

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> node_data = {
        >>>     'name': 'example'
        >>> }
        >>> subnode = nc.create_subnode(node_uid, node_data)
        >>> print('subnode is', subnode)

        **External Documentation**

        关于 `节点的元数据 \
        <https://arkid.docs.apiary.io/#reference/node/6/1>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 NodeClient.create_subnode() 接口与 ArkID 服务端进行交互")
        return self.post(path='{}/node/'.format(node_uid), json_body=json_body)

    def add_subnode(self, node_uid: str, node_uids: list):
        """
        向指定节点添加子节点
        (``PATCH /siteapi/v1/node/<node_uid>/node/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``node_uids`` (*list*)
              节点唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> node_uids = [
        >>>     'node1',
        >>>     'node2',
        >>>         ...
        >>>     'noden'
        >>> ]
        >>> node = nc.add_subnode(node_uid, node_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.add_subnode() 接口与 ArkID 服务端进行交互")
        json_body = {'subject': 'add', 'node_uids': node_uids}
        return self.patch(path='{}/node/'.format(node_uid), json_body=json_body)

    def sort_subnode(self, node_uid: str, node_uids: list):
        """
        对指定子节点按指定位置进行排序
        (``PATCH /siteapi/v1/node/<node_uid>/node/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``node_uids`` (*list*)
              节点唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> node_uids = [
        >>>     'node1',
        >>>     'node2',
        >>>         ...
        >>>     'noden'
        >>> ]
        >>> node = nc.sort_subnode(node_uid, node_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.sort_subnode() 接口与 ArkID 服务端进行交互")
        json_body = {'subject': 'sort', 'node_uids': node_uids}
        return self.patch(path='{}/node/'.format(node_uid), json_body=json_body)

    def query_user_under_node(self, node_uid: str, **params):
        """
        查询指定节点下的直属人员的信息
        (``GET /siteapi/v1/node/<node_uid>/user/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``**params`` (*dict*)
              用户的元信息，参数详情请参考接口文档

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> users = nc.query_user_under_node(node_uid)
        >>> for user in users:
        >>>     print('user is', user)

        **External Documentation**

        关于 `节点的元数据 \
        <https://arkid.docs.apiary.io/#reference/node/7/0>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 NodeClient.query_user_under_node() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/user/'.format(node_uid), params=params)

    def add_user_under_node(self, node_uid: str, user_uids: list):
        """
        向指定节点添加指定成员
        (``PATCH /siteapi/v1/node/<node_uid>/user/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_uids`` (*list*)
              用户唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> user_uids = [
        >>>     'user1',
        >>>     'user2',
        >>>         ...
        >>>     'usern'
        >>> ]
        >>> node = nc.add_user_under_node(node_uid, user_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.add_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'add'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body)

    def delete_user_under_node(self, node_uid: str, user_uids: list):
        """
        从指定节点移除指定成员
        (``PATCH /siteapi/v1/node/<node_uid>/user/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_uids`` (*list*)
              用户唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> user_uids = [
        >>>     'user1',
        >>>     'user2',
        >>>         ...
        >>>     'usern'
        >>> ]
        >>> node = nc.delete_user_under_node(node_uid, user_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.delete_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'delete'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body)

    def override_user_under_node(self, node_uid: str, user_uids: list):
        """
        重置指定节点的指定用户
        (``PATCH /siteapi/v1/node/<node_uid>/user/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_uids`` (*list*)
              用户唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> user_uids = [
        >>>     'user1',
        >>>     'user2',
        >>>         ...
        >>>     'usern'
        >>> ]
        >>> node = nc.override_user_under_node(node_uid, user_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.override_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'override'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body)

    def sort_user_under_node(self, node_uid: str, user_uids: list):
        """
        对指定人按指定位置进行排序
        (``PATCH /siteapi/v1/node/<node_uid>/user/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_uids`` (*list*)
              用户唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> user_uids = [
        >>>     'user1',
        >>>     'user2',
        >>>         ...
        >>>     'usern'
        >>> ]
        >>> node = nc.sort_user_under_node(node_uid, user_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.sort_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'sort'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body)

    def move_out_user_under_node(self, node_uid: str, user_uids: list):
        """
        将这些人从该节点移除，并加到指定节点
        (``PATCH /siteapi/v1/node/<node_uid>/user/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``user_uids`` (*list*)
              用户唯一标识组成的列表

        **Examples**

        >>> nc = arkid_client.NodeClient(...)
        >>> user_uids = [
        >>>     'user1',
        >>>     'user2',
        >>>         ...
        >>>     'usern'
        >>> ]
        >>> node = nc.move_out_user_under_node(node_uid, user_uids)
        >>> print('node is', node)
        """
        self.logger.info("正在调用 NodeClient.move_out_user_under_node() 接口与 ArkID 服务端进行交互")
        json_body = {'user_uids': user_uids, 'subject': 'move_out'}
        return self.patch(path='{}/user/'.format(node_uid), json_body=json_body)
