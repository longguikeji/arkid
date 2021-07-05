from django.urls.base import reverse
from saml2.sigver import CertificateError
from app.models import App
from common.provider import AppTypeProvider
import os
from djangosaml2idp.scripts.idpinit import run as idp_init
from typing import Dict
from djangosaml2idp.scripts.idpinit import BASEDIR


class SAML2IDPAppTypeProvider(AppTypeProvider):

    def create(self, app: App, data: Dict) -> Dict:
        idp_init(app.tenant.uuid)
        data["idp_metadata"] = reverse("api:saml2idp:saml2_idp_metadata",args=(app.tenant.uuid,))

        filename = f"{app.tenant.uuid}_{app.id}"
        xmldata = data.get('xmldata', '')
        entity_id = data.get('entity_id', '')
        cert = data.get('cert', '')
        acs = data.get('acs', '')
        sls = data.get('sls', '')

        if xmldata not in ['', None]:
            with open(BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename, 'w+') as f:
                f.write(xmldata)
        else:
            self.dump_cert(filename, cert)
            try:
                self.gen_xml(filename=filename, entity_id=entity_id, acs=acs, sls=sls)
            except CertificateError:
                raise Exception({'msg': 'perm incorrect'})

        if os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename):
            os.remove(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename)

        return data

    def update(self, app: App, data: Dict) -> Dict:
        idp_init(app.tenant.uuid)
        data["idp_metadata"] = reverse("api:saml2idp:saml2_idp_metadata",args=(app.tenant.uuid,))

        filename = f"{app.tenant.uuid}_{app.id}"
        xmldata = data.get('xmldata', '')
        entity_id = data.get('entity_id', '')
        cert = data.get('cert', '')
        acs = data.get('acs', '')
        sls = data.get('sls', '')

        if xmldata not in ['', None]:
            with open(BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename, 'w+') as f:
                f.write(xmldata)
        else:
            self.dump_cert(filename, cert)
            try:
                self.gen_xml(filename=filename, entity_id=entity_id, acs=acs, sls=sls)
            except CertificateError:
                raise Exception({'msg': 'perm incorrect'})

        if os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename):
            os.remove(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename)
        return data