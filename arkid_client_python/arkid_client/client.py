"""
Define ArkIDClient
"""
from arkid_client.base import BaseClient
from arkid_client.authorizers import BasicAuthorizer
from arkid_client.authorizers import NullAuthorizer
from arkid_client.user import UserClient
from arkid_client.exceptions import ArkIDError


class ArkIDClient(BaseClient):
    """
    由各种 ArkID 客户端集成而生，他提供的所有功能
    都只是各个客户端的简单封装，用来一致对外界用户
    使用;

    当然，如果您足够熟悉本项目，您也可以直接实例化
    您所需要的指定客户端。
    """
    allowed_authorizer_types = [
        BasicAuthorizer,
        NullAuthorizer,
    ]

    def __init__(self, service: str, authorizer=None, *args, **kwargs):
        self.__user_client = None
        BaseClient.__init__(self, service, authorizer=authorizer, *args, **kwargs)

    def __init_client(self, client_class):
        """
        规范所有子客户端集成到 < ArkIDClient > 。由于 < ArkIDClient >
        是由各子客户端组合而成，本身并不提供任何功能。所以，最好将子客户
        端集成的操作流程化。
        """
        classname = client_class.__name__.lower().rstrip('client')
        attr = '_ArkIDClient__{}_client'.format(classname)
        if not hasattr(self, attr):
            raise ArkIDError('无法初始化暂不支持的客户端类型')
        _client = getattr(self, attr)
        if not _client:
            _client = client_class(authorizer=self.authorizer)
            setattr(self, attr, _client)
        return _client

    def query_user(self, **params):
        """
        调用底层 < UserClient > 实例的 query_user 方法
        :param params: 详情见底层说明
        :return:
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.query_user(**params)

    def query_isolated_user(self):
        """
        调用底层 < UserClient > 实例的 query_isolated_user 方法
        :return:
        """

    def create_user(self, json_body: dict):
        """
        调用底层 < UserClient > 实例的 create_user 方法
        :param json_body: 详情见底层说明
        :return:
        """
        self.__user_client = self.__init_client(UserClient)
        return self.__user_client.create_user(json_body)
