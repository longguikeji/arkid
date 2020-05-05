"""
Define PermClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import UsercenterAPIError
from arkid_client.response import ArkIDHTTPResponse


class PermClient(BaseClient):
    """
    权限管理客户端，
    用于与 ArkID 服务端权限管理相关接口的访问操作。

    **Methods**

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
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = UsercenterAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "perm", authorizer=authorizer, **kwargs)

    def query_all_perm(self):
        """
        获取所有权限
        (``GET /siteapi/v1/perm/``)

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_perm()
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.query_all_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='')

    def create_perm(self, json_body: dict):
        """
        创建权限
        (``POST /siteapi/v1/perm/``)

        **Parameters**:

            ``json_body`` (*dict*)

                ``scope`` (*str*)
                  应用 ``uid``

                ``name`` (*str*)
                  应用名称

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = uc.create_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.create_perm() 接口与 ArkID 服务端进行交互")
        return self.post(path='', json_body=json_body)

    def query_perm(self, uid: str):
        """
        获取指定权限
        (``GET /siteapi/v1/perm/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              权限唯一标识

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.query_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(uid))

    def update_perm(self, uid: str, json_body: dict):
        """
        更新指定权限
        (``PATCH /siteapi/v1/perm/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              权限唯一标识

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.update_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.update_perm() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(uid), json_body=json_body)

    def query_perm_owner(self, uid: str, **params):
        """
        获取某权限指定类型的所有者
        该接口内的 ``uid`` ，对于 ``user`` 为 ``username``，对于 ``node`` 为 ``node_uid``
        (``GET /siteapi/v1/perm/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              权限唯一标识

            ``owner_subject`` (*str*)
              权限所有者类型

            ``value`` (*bool*)
              最终判定结果

            ``status`` (*int*)
              授权状态

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_perm_owner(...)
        >>> print('perm is', perm)

        **External Documentation**

        关于 `params 参数\
        <https://arkid.docs.apiary.io/#reference/perm/1/0>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 PermClient.query_perm_owner() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/owner/'.format(uid), params=params)

    def update_perm_owner(self, uid: str, **params):
        """
        更新某权限指定类型的所有者，仅按提供的数据做局部修改
        该接口内的 ``uid`` ，对于 ``user`` 为 ``username``，对于 ``node`` 为 ``node_uid``
        (``PATCH /siteapi/v1/perm/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              权限唯一标识

            ``owner_subject`` (*str*)
              权限所有者类型

            ``value`` (*bool*)
              最终判定结果

            ``status`` (*int*)
              授权状态

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.update_perm_owner(...)
        >>> print('perm is', perm)

        **External Documentation**

        关于 `params 参数\
        <https://arkid.docs.apiary.io/#reference/perm/1/0>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 PermClient.update_perm_owner() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/owner/'.format(uid), params=params)

    def query_specified_user_perm(self, username: str, **params):
        """
        获取用户所有权限,包括所有授权、未授权的权限
        (``GET /siteapi/v1/perm/user/<username>/``)

        **Parameters**:

            ``username`` (*str*)
              用户唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_specified_user_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.query_specified_user_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='user/{}/'.format(username), params=params)

    def update_specified_user_perm(self, username: str, json_body: dict):
        """
        更新用户权限
        (``PATCH /siteapi/v1/perm/user/<username>/``)

        **Parameters**:

            ``username`` (*str*)
              用户唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

            ``json_body`` (*int*)
              权限的部分元信息，详见接口文档

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.update_specified_user_perm(...)
        >>> print('perm is', perm)

        **External Documentation**

        关于 `权限的元数据 \
        <https://arkid.docs.apiary.io/#reference/perm/3/1>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 PermClient.update_specified_user_perm() 接口与 ArkID 服务端进行交互")
        return self.patch(path='user/{}/'.format(username), json_body=json_body)

    def query_dept_perm(self, uid: str, **params):
        """
        获取部门所有权限,包括所有授权、未授权的权限
        (``GET /siteapi/v1/perm/dept/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              部门唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_dept_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.query_dept_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='dept/{}/'.format(uid), params=params)

    def update_dept_perm(self, uid: str, json_body: dict):
        """
        获取部门所有权限,包括所有授权、未授权的权限
        (``PATCH /siteapi/v1/perm/dept/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              部门唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

            ``json_body`` (*dict*)
              权限的元信息,详情参见接口文档

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.update_dept_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.update_dept_perm() 接口与 ArkID 服务端进行交互")
        return self.patch(path='dept/{}/'.format(uid), json_body=json_body)

    def query_group_perm(self, uid: str, **params):
        """
        获取组所有权限,包括所有授权、未授权的权限
        (``GET /siteapi/v1/perm/group/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              组的唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_group_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.query_group_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='group/{}/'.format(uid), params=params)

    def update_group_perm(self, uid: str, json_body: dict):
        """
        获取组所有权限,包括所有授权、未授权的权限
        (``PATCH /siteapi/v1/perm/group/<uid>/``)

        **Parameters**:

            ``uid`` (*str*)
              组唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

            ``json_body`` (*dict*)
              权限的元信息,详情参见接口文档

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.update_group_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.update_group_perm() 接口与 ArkID 服务端进行交互")
        return self.patch(path='group/{}/'.format(uid), json_body=json_body)

    def query_node_perm(self, node_uid: str, **params):
        """
        获取节点所有权限,包括所有授权、未授权的权限
        (``GET /siteapi/v1/perm/node/<uid>/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.query_node_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.query_node_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='node/{}/'.format(node_uid), params=params)

    def update_node_perm(self, node_uid: str, json_body: dict):
        """
        获取组所有权限,包括所有授权、未授权的权限
        (``PATCH /siteapi/v1/perm/node/<uid>/``)

        **Parameters**:

            ``node_uid`` (*str*)
              节点的唯一标识

            ``action`` (*str*)
              特定操作

            ``action_except`` (*bool*)
              排除某操作，惯用``action_except=access``获取应用内权限

            ``scope`` (*int*)
              与应用``uid``对应，惯用该字段获取某应用下权限

            ``json_body`` (*dict*)
              权限的元信息,详情参见接口文档

        **Examples**

        >>> pc = arkid_client.PermClient(...)
        >>> perm = pc.update_node_perm(...)
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 PermClient.update_node_perm() 接口与 ArkID 服务端进行交互")
        return self.patch(path='node/{}/'.format(node_uid), json_body=json_body)
