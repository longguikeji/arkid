"""
Define UcenterClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient
from arkid_client.exceptions import UsercenterAPIError
from arkid_client.response import ArkIDHTTPResponse


class UcenterClient(BaseClient):
    """
    用户中心管理客户端，
    用于与 ArkID 服务端用户中心管理相关接口的访问操作。

    **Methods**

    *  :py:meth:`.view_perm`
    *  :py:meth:`.view_profile`
    *  :py:meth:`.view_current_org`
    *  :py:meth:`.switch_current_org`
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = UsercenterAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, base_url, authorizer=None, **kwargs):
        BaseClient.__init__(self, base_url, "ucenter", authorizer=authorizer, **kwargs)

    def view_perm(self):
        """
        获取用户权限，只返回用户拥有的权限（*只读*）
        (``GET /siteapi/v1/ucenter/perm/``)

        **Examples**

        >>> uc = arkid_client.UsercenterClient(...)
        >>> perm = uc.query_perm()
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 UcenterClient.view_perm() 接口与 ArkID 服务端进行交互")
        return self.get(path='perm/')

    def view_profile(self):
        """
        获取用户自身信息
        (``GET /siteapi/v1/ucenter/profile/``)

        **Examples**

        >>> uc = arkid_client.UsercenterClient(...)
        >>> perm = uc.query_profile()
        >>> print('perm is', perm)
        """
        self.logger.info("正在调用 UcenterClient.view_profile() 接口与 ArkID 服务端进行交互")
        return self.get(path='profile/')

    def view_current_org(self):
        """
        获取用户当前所在组织的信息
        (``GET /siteapi/v1/ucenter/org/``)

        **Examples**

        >>> oc = arkid_client.UsercenterClient(...)
        >>> org = oc.get_current_org()
        >>> print('org: ', org)
        """
        self.logger.info("正在调用 UcenterClient.view_current_org() 接口与 ArkID 服务端进行交互")
        return self.get(path='org/')

    def switch_current_org(self, json_body: dict):
        """
        切换用户当前所在的组织
        (``PUT /siteapi/v1/ucenter/org/``)

        **Parameters**:

            ``json_body`` (*dict*)

                ``oid`` (*str*)
                  组织的唯一标识

        **Examples**

        >>> oc = arkid_client.UsercenterClient(...)
        >>> org = oc.switch_current_org({'oid': 'example'})
        >>> print('org: ', org)
        """
        self.logger.info("正在调用 UcenterClient.switch_current_org() 接口与 ArkID 服务端进行交互")
        return self.put(path='org/', json_body=json_body)

    def query_apps(self, **params):
        """
        普通用户获取可见应用列表
        (``GET /siteapi/v1/ucenter/apps/``)

        **Parameters**:

            ``name`` (*str*)
              应用名称

        **Examples**

        >>> oc = arkid_client.UsercenterClient(...)
        >>> apps = oc.query_apps()
        >>> print('apps: ', apps)
        """
        self.logger.info("正在调用 UcenterClient.query_apps() 接口与 ArkID 服务端进行交互")
        return self.get(path='apps/', params=params)
