"""
SAML2协议 SP注册
"""
import base64
import time
import logging
from django.urls.base import reverse
from common.provider import ExternalIdpProvider
from config import get_app_config

logger = logging.Logger(__name__)


class Saml2SPExternalIdpProvider(ExternalIdpProvider):
    """
    SAML2协议 IDP server App
    """

    def create(self, tenant_uuid, external_idp, data):  # pylint: disable=arguments-differ，unused-argument
        """
        创建
        """

        # 此处是网上随意找的
        data["img_url"] = data.get(
            "img_url", "https://img2.baidu.com/it/u=301558167,4277299842&fm=26&fmt=auto&gp=0.jpg")

        data["sp_metadata_file"] = f'{get_app_config().get_host()}{reverse("api:saml2sp:sp_download_metadata",args=(tenant_uuid,))}'

        data["login_url"] = f'{get_app_config().get_host()}{reverse("api:saml2sp:sp_login",args=(tenant_uuid,))}'


        idp_xmldata_file = data.get("idp_xmldata_file")

        idp_xmldata = idp_xmldata_file.replace("data:text/xml;base64,", "")
        idp_xmldata = base64.b64decode(idp_xmldata)
        idp_xmldata = idp_xmldata.decode()

        idp_xmldata_file_path = f"{BASE_DIR}/djangosaml2sp/saml2_config/IDP_metadata.xml"
        with open(idp_xmldata_file_path,"w") as f:
            f.write(idp_xmldata)

        return data

    def get_groups(self):
        """
        ExternalIDP => ArkID
        """

    def get_users(self):
        """
        ExternalIDP => ArkID
        """
