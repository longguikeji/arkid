"""
Define AppClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import NodeAPIError, ArkIDSDKUsageError
from arkid_client.response import ArkIDHTTPResponse


class AppClient(BaseClient):
    """
    应用管理客户端，用于与 ArkID 服务端应用管理相关
    接口的访问操作。

    **Methods**

    *  :py:meth:`.query_app_list`
    *  :py:meth:`.create_app`
    *  :py:meth:`.query_app`
    *  :py:meth:`.update_app`
    *  :py:meth:`.delete_app`
    *  :py:meth:`.register_app`
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = NodeAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "org", authorizer=authorizer, **kwargs)

    def query_app_list(self, oid: str, **params):
        """
        获取应用信息列表
        (``GET /siteapi/v1/org/<oid>/app/``)

        **Parameters**:

            ``name`` (*str*)
              查询关键字，进行用户名、姓名、邮箱、手机号模糊搜索

            ``node_uid`` (*str*)
              查询该节点的权限

            ``user_uid`` (*int*)
              查询该用户权限

            ``owner_access`` (*Boolean*)
              限定访问权限结果

        **Examples**

        >>> ac = arkid_client.AppClient(...)
        >>> apps = ac.query_app_list(...)
        >>> for app in apps:
        >>>     print(app['name'], 'uid: '
        >>>           ,app['uid'])
        """
        self.logger.info("正在调用 AppClient.query_app_list() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/app/'.format(oid), params=params)

    def create_app(self, oid: str, json_body: dict):
        """
        创建应用
        (``POST /siteapi/v1/org/<oid>/app/``)

        **Parameters**:
            json_body (*dict*)
              应用的元信息, 参数详情请参考接口文档
        **Examples**

        >>> ac = arkid_client.AppClient(...)
        >>> app = ac.create_app(...)
        >>> print('app is', app)

        **External Documentation**

        关于 `应用的元数据 \
        <https://arkid.docs.apiary.io/#reference/app/0/1>`_
        详情请参阅API文档。
        """
        self.logger.info("正在调用 AppClient.create_app() 接口与 ArkID 服务端进行交互")
        return self.post(path='{}/app/'.format(oid), json_body=json_body)

    def query_app(self, oid: str, uid: str):
        """
        获取特定应用
        (``GET /siteapi/v1/org/<oid>/app/<uid>/``)

        **Parameters**:

            ``oid`` (*str*)
              组织的唯一标识

            ``uid`` (*str*)
              应用的唯一标识

        **Examples**

        >>> ac = arkid_client.AppClient(...)
        >>> app = ac.query_app()
        >>> print('app: ', app)
        """
        self.logger.info("正在调用 AppClient.query_app() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/app/{}/'.format(oid, uid))

    def update_app(self, oid: str, uid: str, json_body: dict):
        """
        修改特定应用
        (``PATCH /siteapi/v1/org/<oid>/app/<uid>/``)

        **Parameters**:

            ``oid`` (*str*)
              组织的唯一标识

            ``uid`` (*str*)
              应用的唯一标识

        **Examples**

        >>> ac = arkid_client.AppClient(...)
        >>> app = ac.update_app(...)
        >>> print('app: ', app)
        """
        self.logger.info("正在调用 AppClient.update_app() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/app/{}/'.format(oid, uid), json_body=json_body)

    def delete_app(self, oid: str, uid: str):
        """
        修改特定应用
        (``DELETE /siteapi/v1/org/<oid>/app/<uid>/``)

        **Parameters**:

            ``oid`` (*str*)
              组织的唯一标识

            ``uid`` (*str*)
              应用的唯一标识

        **Examples**

        >>> ac = arkid_client.AppClient(...)
        >>> app = ac.delete_app(...)
        """
        self.logger.info("正在调用 AppClient.delete_app() 接口与 ArkID 服务端进行交互")
        return self.delete(path='{}/app/{}/'.format(oid, uid))

    def register_app(self, oid: str, uid: str,  protocol: str, json_body: dict):
        """
        注册应用
        (``PATCH /siteapi/v1/org/<oid>/app/<uid>/*/``)

        **Parameters**:

            ``oid`` (*str*)
              组织的唯一标识

            ``uid`` (*str*)
              应用的唯一标识

            ``protocol`` (*str*)
              应用所采用的协议

            ``json_body`` (*dict*)
              应用的元信息

        **Examples**

        >>> ac = arkid_client.AppClient(...)
        >>> app = ac.register_app(...)
        >>> print('app: ', app)
        """
        protocols_map = {
            'oauth': 'oauth/',
        }
        if protocol not in protocols_map:
            self.logger.info("无法注册应用， 暂不支持的协议类型")
            raise ArkIDSDKUsageError('无法注册应用，暂不支持的操作类型(invalid protocol)')
        self.logger.info("正在调用 AppClient.register_app() 接口与 ArkID 服务端进行交互")
        return self.post(path='{}/app/{}/{}/'.format(oid, uid, protocols_map[protocol]), json_body=json_body)

