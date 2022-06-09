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
from six import text_type

class Saml2IdpProvider(BaseIdpProvider):
    
    def sp_config(self, app:App, data: dict):
        
        f_name = f"{app.tenant.uuid}_{app.id}"
        try:
            self.dump_cert(f_name,data.pop("cert",None))
        except Exception:
            pass
        
        data["idp_cert"] = get_app_config().get_frontend_host() + \
            reverse(
                "api:saml2:idp_cert",
            args=(
                app.tenant.uuid,
            )
        )
            
        self.gen_sp_metadata(
            app.tenant.uuid,
            app.id,
            data.get("entity_id"),
            data.get("acs",""),
            data.get("sls","")
        )
        
        return data

    def dump_cert(self, filename, cert) -> None:
        """
        写入sp验证文件
        """
        if cert not in ["", None]:
            cert = cert.replace("data:application/pkix-cert;base64,", "")
            cert = base64.b64decode(cert)
            cert = cert.decode()
            with open(os.path.join(CERT_BASEDIR, f'{filename}.crt'), "w") as f:
                f.write(cert)
    
    def gen_sp_metadata(self,tenant_uuid, app_id, entity_id, acs, sls):    # pylint: disable=no-self-use
        '''将SAMLAPP配置写入指定路径xml文件
        '''
        f_name = f"{tenant_uuid}_{app_id}"
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
                        "assertion_consumer_service": [(acs, BINDING_HTTP_POST)],
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