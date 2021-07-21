"""
SAML2协议 SP注册
"""
import logging
from common.provider import ExternalIdpProvider

logger = logging.Logger(__name__)


class Saml2SPExternalIdpProvider(ExternalIdpProvider):
    """
    SAML2协议 IDP server App
    """

    def create(self, tenant_uuid, external_idp, data):  # pylint: disable=arguments-differ，unused-argument
        """
        创建
        """

        return data

    def update(self, tenant_uuid, external_idp, data):  # pylint: disable=arguments-differ，unused-argument
        """
        更新
        """
        return data

    def delete(self):
        """
        删除APP
        """
        print(self)
        return super().delete()
