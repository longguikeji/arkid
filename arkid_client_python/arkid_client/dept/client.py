"""
Define DeptClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient, reload_service
from arkid_client.exceptions import DeptAPIError
from arkid_client.response import ArkIDHTTPResponse


class DeptClient(BaseClient):
    """
    部门管理客户端，用于与 ArkID 服务端部门管理相关
    接口的访问操作。
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = DeptAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, authorizer=None, **kwargs):
        BaseClient.__init__(self, "dept", authorizer=authorizer, **kwargs)

    def query_dept(self, **params):
        """
        查询部门列表

        :param params:

            ``name`` (*str*)
              部门名称

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 DeptClient.query_dept() 接口与 ArkID 服务端进行交互")
        return self.get(path='', params=params)

    def query_specified_dept(self, uid: str):
        """
        查看指定部门的信息
        :param uid: 部门的唯一标识， root 特指全公司。
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 DeptClient.query_specified_dept() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(uid))

    def update_specified_dept(self, uid: str, json_body: dict):
        """
        修改指定部门的信息
        :param uid: 部门的唯一标识
        :param json_body: 部门的元信息, 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 DeptClient.update_specified_dept() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(uid), json_body=json_body)

    def delete_specified_dept(self, uid: str):
        """
        删除指定部门的信息
        :param uid: 部门的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 DeptClient.delete_specified_dept() 接口与 ArkID 服务端进行交互")
        return self.delete(path='{}/'.format(uid))
