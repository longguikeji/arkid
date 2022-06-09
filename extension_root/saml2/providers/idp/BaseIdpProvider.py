from abc import abstractmethod
import os
from typing import Dict

from django.urls import reverse
from app.models import App
from common.provider import AppTypeProvider
from config import get_app_config
from ...common.certs import check_self_signed_cert
from ...common.metadata import BASEDIR as MD_BASEDIR
import copy
from six import text_type
from ...idp import idpsettings
from saml2.config import IdPConfig
from saml2.metadata import entity_descriptor


class BaseIdpProvider(AppTypeProvider):

    def create(self, app: App, data: Dict) -> Dict:  # pylint: disable=arguments-differ
        """
        创建APP
        """
        tenant = app.tenant
        self.create_idp_metadata(tenant.uuid,app.id)
        data = self.sp_config(app, data)
        data = self.config_data(app,data)
        return data

    def update(self, app: App, data: Dict) -> Dict:  # pylint: disable=arguments-differ
        """
        更新APP
        """
        tenant = app.tenant
        self.create_idp_metadata(tenant.uuid,app.id)
        data = self.sp_config(app, data)
        data = self.config_data(app, data)
        return data

    def delete(self):
        """
        删除APP
        """
        return super().delete()
    
    def config_data(self,app:App,data:dict):
        """配置数据处理

        Args:
            app (App): 应用对象
            data (dict): 数据
        """         
        data["idp_sso_url"] = get_app_config().get_frontend_host() + f'{reverse("api:saml2:idp_sso_redirect",args=(app.tenant.uuid,app.id))}'
        data["idp_entity_id"] = get_app_config().get_frontend_host() + f'{reverse("api:saml2:idp_metadata",args=(app.tenant.uuid,app.id))}'
        return data
    
    def create_idp_metadata(self, tenant_id,app_id):
        '''配置IdP,生成证书、元数据文件'''
        check_self_signed_cert(tenant_uuid=tenant_id)

        file_path = os.path.join(
            MD_BASEDIR,
            f'{tenant_id}_{app_id}_idp.xml'
        )
        if not os.path.exists(
            file_path
        ):
            conf = IdPConfig()    # pylint: disable=invalid-name
            conf.load(
                copy.deepcopy(
                    idpsettings.get_saml_idp_config(
                        tenant_id,
                        app_id
                    )
                )
            )
            meta_data = entity_descriptor(conf)    # pylint: disable=invalid-name
            content = text_type(meta_data).encode('utf-8')
            with open(file_path, 'wb') as f:
                f.write(content)
    
    @abstractmethod
    def sp_config(self, app:App, data:dict):
        """sp属性配置处理

        Args:
            data (dict): 数据
        """
        pass