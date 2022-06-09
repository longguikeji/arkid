import base64
import copy
import os
from django.urls import reverse
from app.models import App
from config import get_app_config
from .BaseIdpProvider import BaseIdpProvider
from ...common.metadata import BASEDIR as MD_BASEDIR

class Saml2IdpFileProvider(BaseIdpProvider):
    
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
        
        return data
    
    def save_metadata(self, f_name, metadata):
        file_path = os.path.join(
            MD_BASEDIR,
            f'{f_name}_sp.xml'
        )
        with open(file_path,'w') as f:
            f.write(metadata)