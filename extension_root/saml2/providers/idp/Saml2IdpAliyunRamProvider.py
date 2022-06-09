from asyncio.log import logger
import base64
import copy
import os
from django.urls import reverse
from app.models import App
from config import get_app_config
from .BaseIdpProvider import BaseIdpProvider
from ...common.certs import BASEDIR as CERT_BASEDIR
from ...common.metadata import BASEDIR as MD_BASEDIR
from saml2.config import SPConfig
from saml2.entity_category.edugain import COC
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.sigver import get_xmlsec_binary
from saml2.saml import NAME_FORMAT_URI
from saml2.metadata import entity_descriptor
from saml2.mdstore import MetaDataFile
from six import text_type

class Saml2IdpAliyunRamProvider(BaseIdpProvider):
    
    def sp_config(self, app:App, data: dict):
        f_name = f"{app.tenant.uuid}_{app.id}"
        data["idp_metadata"] = get_app_config().get_frontend_host() + \
            reverse(
                "api:saml2:idp_metadata",
            args=(
                app.tenant.uuid,
                app.id
            )
        )
            
        xmldata_file = data.get("xmldata_file",None)
        
        if xmldata_file not in ["", None]:
            data.pop('xmldata_file')
            xmldata_file = xmldata_file.replace("data:text/xml;base64,", "")
            xmldata = base64.b64decode(xmldata_file)
            xmldata = xmldata.decode()
            self.save_metadata(
                f_name,
                xmldata
            )
            data["xmldata"] = xmldata
            
        data = self.read_sp_metadata(data,f_name)
        
        data["attribute_mapping"] = app.data.get("attribute_mapping",{})
        if data.get('role',None):
            data["attribute_mapping"]["https://www.aliyun.com/SAML-Role/Attributes/Role"] = data["role"]
        if data.get('role_session_name',None):
            data["attribute_mapping"]["https://www.aliyun.com/SAML-Role/Attributes/RoleSessionName"] = data["role_session_name"]
        if data.get('session_duration',None):
            data["attribute_mapping"]["https://www.aliyun.com/SAML-Role/Attributes/SessionDuration"] = data["session_duration"]
        
        app.url = f'{get_app_config().get_frontend_host()}{reverse("api:saml2:idp_sso_init",args=(app.tenant.uuid,app.id))}?spauthn='+'{token}'
        app.save()
        return data
    
    def save_metadata(self, f_name, metadata):
        file_path = os.path.join(
            MD_BASEDIR,
            f'{f_name}_sp.xml'
        )
        with open(file_path,'w') as f:
            f.write(metadata)
            
    def read_sp_metadata(self,data:dict,filename:str):
        """ 读取sp metadata信息

        Args:
            data (dict): 外部传入数据
            filename (_type_): metadata文件名称
        Returns:
            dict: 外部传入数据
        """
        try:
            filename = os.path.join(
                MD_BASEDIR,
                f'{filename}_sp.xml'
            )
            sp_metadatafile = MetaDataFile(attrc=None, filename=filename)
            sp_metadatafile.load()
            sp_entity = sp_metadatafile.entity[list(sp_metadatafile.keys())[0]]

            data["entity_id"] = sp_entity["entity_id"]

            spsso_descriptor = sp_entity["spsso_descriptor"][0]
            data["acs"] = spsso_descriptor["assertion_consumer_service"][0]["location"]
            try:
                data["sls"] = spsso_descriptor["single_logout_service"][0]["location"]
            except Exception as err:
                logger.error(err)
            data["cert"] = spsso_descriptor["key_descriptor"][0]["key_info"]["x509_data"][0]["x509_certificate"]["text"]

        except Exception as err:  # pylint: disable=broad-except
            print(err)
            raise Exception({'msg': '元数据文件解析出错'}) 
        return data