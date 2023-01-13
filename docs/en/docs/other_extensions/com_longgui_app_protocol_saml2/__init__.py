import base64
import copy
import os
from django.urls import reverse
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.translation import gettext_default as _
from arkid.core.models import App, Tenant
from arkid.extension.models import TenantExtensionConfig
from arkid.config import get_app_config
from arkid.common.logger import logger
from .constants import package
from .schema import Saml2SPCertConfigSchema,Saml2SPAliyunRamConfigSchema,Saml2SPAliyunRoleConfigSchema,Saml2SPMetadataFileConfigSchema
from .urls import urlpatterns as urls
from saml2.config import SPConfig
from saml2.entity_category.edugain import COC
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.sigver import get_xmlsec_binary
from saml2.saml import NAME_FORMAT_URI
from saml2.metadata import entity_descriptor
from .idp import idpsettings
from saml2.config import IdPConfig
from saml2.mdstore import MetaDataFile
from .common.certs import BASEDIR as CERT_BASEDIR, check_self_signed_cert
from .common.metadata import BASEDIR as MD_BASEDIR
from six import text_type
from arkid.core import api as core_api, event as core_event

class Saml2Extension(AppProtocolExtension):
    def load(self):
        # 加载相应的配置文件
        self.register_app_protocol_schema(Saml2SPCertConfigSchema, 'Saml2SP_CERT')
        self.register_app_protocol_schema(Saml2SPMetadataFileConfigSchema, 'Saml2SP_METADATA')
        self.register_app_protocol_schema(Saml2SPAliyunRamConfigSchema, 'Saml2SP_AliyunRam')
        self.register_app_protocol_schema(Saml2SPAliyunRoleConfigSchema, 'Saml2SP_AliyunRole')

        self.listen_event(core_event.APP_CONFIG_DONE, self.config_done)
        
        self.load_urls()
        super().load()
    
    def create_app(self, event, **kwargs):
        return True

    def update_app(self, event, **kwargs):
        return True

    def delete_app(self, event, **kwargs):

        # 判断是否存在配置，入无运行时配置则跳过
        if not event.data.config:
            return

        f_name = f"{event.data.tenant.id}_{event.data.config.id}"
        sp_cert_path =os.path.join(
            CERT_BASEDIR,
            f'{f_name}_sp.crt'
        )
        if os.path.exists(
            sp_cert_path
        ):
            os.path.remove(sp_cert_path)
            
        sp_metadata_path = os.path.join(
            MD_BASEDIR,
            f'{f_name}_sp.xml'
        )
        if os.path.exists(
            sp_metadata_path
        ):
            os.remove(sp_metadata_path)
            
        idp_metadata_path = os.path.join(
            MD_BASEDIR,
            f'{f_name}_idp.xml'
        )
        if os.path.exists(
            idp_metadata_path
        ):
            os.remove(idp_metadata_path)
    
    def config_done(self,event,**kwargs):
        if not event.data.url:
            app = event.data
            host = get_app_config().get_frontend_host()
            namespace = f'api:{self.pname}_tenant'
            app.url = host+reverse(namespace+":idp_sso_init", args=[app.tenant.id,app.config.id])
            app.save()
    
    def update_tenant_config(self, id, config, name, type):
        config["type"] = type
        tenantextensionconfig = TenantExtensionConfig.valid_objects.filter(id=id).first()
        config = self.gen_idp_data(
            tenant_id=tenantextensionconfig.tenant.id,
            config_id=id,
            config=config
        )
        config = self.gen_sp_data(tenantextensionconfig.tenant.id,id,config)
        return super().update_tenant_config(id, config, name, type)
    
    def create_tenant_config(self, tenant, config, name, type):
        config["type"] = type
        tenantextensionconfig = super().create_tenant_config(tenant, config, name, type)
        config = self.gen_idp_data(
            tenant_id=tenantextensionconfig.tenant.id,
            config_id=tenantextensionconfig.id,
            config=config
        )
        config = self.gen_sp_data(tenantextensionconfig.tenant.id,tenantextensionconfig.id,config)
        tenantextensionconfig.config = config
        tenantextensionconfig.save()
        return tenantextensionconfig
    
    def gen_sp_data(self, tenant_id:str, config_id:str, config:dict):
        if config.get("sp_metadata",None) not in ["",None]:
            self.dump_sp_metadata(
                tenant_id,
                config_id,
                config["sp_metadata"]
            )
            
            config = self.read_sp_metadata(
                tenant_id,
                config_id,
                config
            )
        else:
            sp_cert = config.get("sp_cert")
            self.dump_sp_cert(tenant_id,config_id,sp_cert)
            self.gen_sp_metadata(
                tenant_id,
                config_id,
                config.get("sp_entity_id"),
                config.get("sp_acs"),
                config.get("sp_sls","")
            )
            
        # 处理attribute_mapping
        config["attribute_mapping"] = config.get("attribute_mapping",{})
        if config["type"] == "Saml2SP_AliyunRole":
            # 阿里云角色SSO
            if config.get('role',None):
                config["attribute_mapping"]["https://www.aliyun.com/SAML-Role/Attributes/Role"] = config["role"]
            if config.get('role_session_name',None):
                config["attribute_mapping"]["https://www.aliyun.com/SAML-Role/Attributes/RoleSessionName"] = config["role_session_name"]
            if config.get('session_duration',None):
                config["attribute_mapping"]["https://www.aliyun.com/SAML-Role/Attributes/SessionDuration"] = config["session_duration"]
        
        return config

    def gen_idp_data(self,tenant_id:str, config_id:str, config:dict):
        host = get_app_config().get_frontend_host()
        namespace = f'api:{self.pname}_tenant'
        config["namespace"] = namespace
        config["idp_cert"] = host+reverse(namespace+":idp_cert", args=[tenant_id])
        config["idp_metadata"] = host+reverse(namespace+":idp_metadata", args=[tenant_id,config_id])
        config["idp_sso_url"] = host+reverse(namespace+":idp_sso_redirect", args=[tenant_id,config_id])
        self.create_idp_metadata(
            tenant_id,
            config_id,
            namespace
        )
        return config
    
    def gen_sp_metadata(self,tenant_uuid, config_id, entity_id, acs, sls):    # pylint: disable=no-self-use
        '''将SAMLAPP配置写入指定路径xml文件
        '''
        f_name = f"{tenant_uuid}_{config_id}"
        conf = SPConfig()
        endpointconfig = {
            "entityid": entity_id,
            'entity_category': [COC],
            "description": "extra SP setup",
            "service": {
                "sp": {
                    "want_response_signed": False,
                    "authn_requests_signed": True,
                    "logout_requests_signed": True,
                    "endpoints": {
                        "assertion_consumer_service": [(acs,BINDING_HTTP_REDIRECT),(acs,BINDING_HTTP_POST)],
                        "single_logout_service": [
                            (sls, BINDING_HTTP_REDIRECT),
                            (sls.replace('redirect', 'post'), BINDING_HTTP_POST),
                        ],
                    }
                },
            },
            "cert_file": os.path.join(CERT_BASEDIR, f'{f_name}.crt'),
            "xmlsec_binary": get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
            "metadata": {
                # "local": [os.path.join(MD_BASEDIR, f'{f_name}_idp.xml')]
            },
            "name_form": NAME_FORMAT_URI,
        }
        conf.load(copy.deepcopy(endpointconfig))
        meta_data = entity_descriptor(conf)
        content = text_type(meta_data).encode('utf-8')
        with open(MD_BASEDIR + '%s_sp.xml' % f_name, 'wb+') as f:
            f.write(content)
    
    def create_idp_metadata(self, tenant_id,config_id,namespace):
        '''配置IdP,生成证书、元数据文件'''
        check_self_signed_cert(tenant_uuid=tenant_id)

        file_path = os.path.join(
            MD_BASEDIR,
            f'{tenant_id}_{config_id}_idp.xml'
        )
        if not os.path.exists(
            file_path
        ):
            conf = IdPConfig()    # pylint: disable=invalid-name
            conf.load(
                copy.deepcopy(
                    idpsettings.get_saml_idp_config(
                        tenant_id,
                        config_id,
                        namespace
                    )
                )
            )
            meta_data = entity_descriptor(conf)    # pylint: disable=invalid-name
            content = text_type(meta_data).encode('utf-8')
            with open(file_path, 'wb') as f:
                f.write(content)
    
    def dump_sp_cert(self, tenant_id:str, config_id:str, cert) -> None:
        """
        写入sp验证文件
        """
        file_name = f"{tenant_id}_{config_id}"
        if cert not in ["", None]:
            cert = cert.replace("data:application/pkix-cert;base64,", "")
            cert = base64.b64decode(cert)
            cert = cert.decode()
            with open(os.path.join(CERT_BASEDIR, f'{file_name}.crt'), "w") as f:
                f.write(cert)
    
    def dump_sp_metadata(self, tenant_id, config_id, metadata):
        xmldata_file = metadata.replace("data:text/xml;base64,", "")
        xmldata = base64.b64decode(xmldata_file)
        xmldata = xmldata.decode()
        f_name = f"{tenant_id}_{config_id}"
        file_path = os.path.join(
            MD_BASEDIR,
            f'{f_name}_sp.xml'
        )
        with open(file_path,'w') as f:
            f.write(xmldata)
    
    def read_sp_metadata(self,tenant_id,config_id,config):
        try:
            filename = os.path.join(
                MD_BASEDIR,
                f'{tenant_id}_{config_id}_sp.xml'
            )
            sp_metadatafile = MetaDataFile(attrc=None, filename=filename)
            sp_metadatafile.load()
            sp_entity = sp_metadatafile.entity[list(sp_metadatafile.keys())[0]]

            config["entity_id"] = sp_entity["entity_id"]

            spsso_descriptor = sp_entity["spsso_descriptor"][0]
            config["acs"] = spsso_descriptor["assertion_consumer_service"][0]["location"]
            try:
                config["sls"] = spsso_descriptor["single_logout_service"][0]["location"]
            except Exception as err:
                logger.error(err)
            config["cert"] = spsso_descriptor["key_descriptor"][0]["key_info"]["x509_data"][0]["x509_certificate"]["text"]

        except Exception as err:  # pylint: disable=broad-except
            print(err)
            raise Exception({'msg': '元数据文件解析出错'}) 
        return config
    
    def load_urls(self):
        self.register_routers(urls, True)
        
extension = Saml2Extension()
