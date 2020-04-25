"""
Define OrgClient
"""
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.base import BaseClient, reload_service
from arkid_client.exceptions import OrgAPIError
from arkid_client.response import ArkIDHTTPResponse


class OrgClient(BaseClient):
    """
    组织管理客户端，用于与 ArkID 服务端组织管理相关
    接口的访问操作。
    """
    allowed_authorizer_types = [BasicAuthorizer]
    error_class = OrgAPIError
    default_response_class = ArkIDHTTPResponse

    def __init__(self, authorizer=None, **kwargs):
        BaseClient.__init__(self, "org", authorizer=authorizer, **kwargs)

    def query_own_org(self, **params):
        """
        查询用户所在的组织

        :param params:

            ``role`` (*str*)
              在组织内的角色

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.query_own_org() 接口与 ArkID 服务端进行交互")
        return self.get(path='', params=params)

    def query_specified_org(self, oid: str):
        """
        查看指定组织的信息
        :param oid: 组织的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.query_specified_org() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/'.format(oid))

    def create_org(self, json_body: dict):
        """
        创建组织
        :param json_body: 组织的元信息， 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.create_org() 接口与 ArkID 服务端进行交互")
        return self.post(path='', json_body=json_body)

    def delete_specified_org(self, oid: str):
        """
        删除指定组织的信息
        :param oid: 组织的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.delete_specified_org() 接口与 ArkID 服务端进行交互")
        return self.delete(path='{}/'.format(oid))

    def update_specified_org(self, oid: str, json_body: dict):
        """
        修改指定组织的信息

        :param oid: 组织的唯一标识
        :param json_body: 组织的元信息, 参数详情请参考接口文档
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.update_specified_org() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/'.format(oid), json_body=json_body)

    def query_orguser(self, oid: str, **params):
        """
        查看特定组织的成员信息
        :param oid: 组织的唯一标识
        :param params:

            ``page`` (*int*)
              Default: 1

            ``page_size`` (*int*)
              Default: 30

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.query_orguser() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/user/'.format(oid), params=params)

    def update_orguser(self, oid: str, json_body: dict):
        """
        编辑指定组织的成员结构
        :param oid: 组织的唯一标识
        :param json_body:

            ``subject`` (*enum* & *str*)
              1) add: 向组织中增加成员
              2) delete: 从组织中移除成员

            ``usernames`` (*list[*str*]*)
              Default: 30

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.update_orguser() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/user/'.format(oid), json_body=json_body)

    def query_specified_orguser(self, oid: str, username: str):
        """
        查看指定组织的指定成员的信息
        :param oid: 组织的唯一标识
        :param username: 用户唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.query_specified_orguser() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/user/{}/'.format(oid, username))

    def update_specified_orguser(self, oid: str, username: str, json_body: dict):
        """
        编辑指定组织的指定成员的信息
        :param oid: 组织的唯一标识
        :param username: 用户唯一标识
        :param json_body:

            ``email`` (*str*)
              成员邮箱

            ``employee_number`` (*str*)
              成员工号

            ``position`` (*str*)
              成员职位

            ``hiredate`` (*str*)
              成员雇佣日期

            ``remark`` (*str*)
              成员备注

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.update_specified_orguser() 接口与 ArkID 服务端进行交互")
        return self.patch(path='{}/user/{}/'.format(oid, username), json_body=json_body)

    def get_org_invitation_key(self, oid: str):
        """
        获取指定组织邀请用的最新的密钥
        :param oid: 组织的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.get_org_invitation_key() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/invitation/'.format(oid))

    def refresh_org_invitation_key(self, oid: str):
        """
        刷新指定组织邀请用的最新的密钥
        :param oid: 组织的唯一标识
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.get_org_invitation_key() 接口与 ArkID 服务端进行交互")
        return self.put(path='{}/invitation/'.format(oid))

    def view_org_by_invitation_key(self, oid: str, invite_link_key: str):
        """
        使用邀请密钥查看指定组织的信息
        :param oid: 组织的唯一标识
        :param invite_link_key: 组织邀请密钥
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.view_org_by_invitation_key() 接口与 ArkID 服务端进行交互")
        return self.get(path='{}/invitation/{}/'.format(oid, invite_link_key))

    def join_org_by_invitation_key(self, oid: str, invite_link_key: str):
        """
        使用邀请密钥加入指定组织
        :param oid: 组织的唯一标识
        :param invite_link_key: 组织邀请密钥
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.join_org_by_invitation_key() 接口与 ArkID 服务端进行交互")
        return self.post(path='{}/invitation/{}/'.format(oid, invite_link_key))

    @reload_service('ucenter')
    def get_current_org(self):
        """
        获取用户当前所在组织的信息
        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.get_current_org() 接口与 ArkID 服务端进行交互")
        return self.get(path='org/')

    @reload_service('ucenter')
    def switch_current_org(self, json_body: dict):
        """
        切换用户当前所在的组织
        :param json_body:

            ``oid`` (*str*)
              组织的唯一标识

        :return: :class: < ArkIDHTTPResponse > object
        """
        self.logger.info("正在调用 OrgClient.switch_current_org() 接口与 ArkID 服务端进行交互")
        return self.put(path='org/', json_body=json_body)
