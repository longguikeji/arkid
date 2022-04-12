"""
SAML2协议 SP注册
"""
import base64
import logging
import os
from typing import Dict
from django.db.models import base
from django.urls.base import reverse
from saml2.mdstore import MetaDataFile
from saml2.sigver import CertificateError
from app.models import App
from common.provider import AppTypeProvider
from djangosaml2idp.scripts.idpinit import run as idp_init
from djangosaml2idp.scripts.idpinit import BASEDIR
from djangosaml2idp.scripts.idpclear import run as idpclear
from config import get_app_config

logger = logging.Logger(__name__)


class SAML2IDPAppTypeProvider(AppTypeProvider):
    """
    SAML2协议 IDP server App
    """

    def create(self, app: App, data: Dict) -> Dict:  # pylint: disable=arguments-differ
        """
        创建APP
        """
        try:
            idp_init(app.tenant.uuid, app.id)
        except Exception as err:  # pylint: disable=broad-except
            logger.debug(
                f"idp初始化出错:{err}")  # pylint: disable=logging-fstring-interpolation
            idpclear(app.tenant.uuid, app.id)
            raise err

        data["idp_metadata"] = get_app_config().get_host() + \
            reverse("api:saml2idp:download_metadata",
                    args=(app.tenant.uuid, app.id))

        xmldata_file = data.get("xmldata_file", None)
        if xmldata_file not in ["", None]:
            xmldata_file = xmldata_file.replace("data:text/xml;base64,", "")
            data["xmldata"] = base64.b64decode(xmldata_file)
            data["xmldata"] = data["xmldata"].decode()

        filename = f"{app.tenant.uuid}_{app.id}"
        filename = BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename
        xmldata = data.get('xmldata', '')
        entity_id = data.get('entity_id', '')
        cert = data.get('cert', '')
        acs = data.get('acs', '')
        sls = data.get('sls', '')

        if xmldata not in ['', None]:
            with open(filename, 'w') as f:
                f.write(xmldata)
        else:
            self.dump_cert(filename, cert)
            try:
                self.gen_xml(
                    filename=filename,
                    entity_id=entity_id,
                    acs=acs,
                    sls=sls
                )
            except CertificateError:
                raise Exception({'msg': 'perm incorrect'}
                                )  # pylint: disable=raise-missing-from

        try:
            sp_metadatafile = MetaDataFile(attrc=None, filename=filename)
            sp_metadatafile.load()
            sp_entity = sp_metadatafile.entity[list(sp_metadatafile.keys())[0]]

            if entity_id in ["", None]:
                data["entity_id"] = sp_entity["entity_id"]

            spsso_descriptor = sp_entity["spsso_descriptor"][0]
            if acs in ["", None]:
                data["acs"] = spsso_descriptor["assertion_consumer_service"][0]["location"]
            try:
                if sls in ["", None]:
                    data["sls"] = spsso_descriptor["single_logout_service"][0]["location"]
            except Exception as err:
                print(err)
                pass

            if cert in ["", None]:
                data["cert"] = spsso_descriptor["key_descriptor"][0]["key_info"]["x509_data"][0]["x509_certificate"]["text"]

        except Exception as err:  # pylint: disable=broad-except
            print(err)
            raise Exception({'msg': '元数据文件解析出错'}
                            )  # pylint: disable=raise-missing-from

        if os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename):
            os.remove(
                BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename)

        app.url = f'{reverse("api:saml2idp:saml_sso_hook",args=(app.tenant.uuid,app.id))}?spauthn='+'{token}'

        if data.get("sso_url", None) in ["", None]:
            data["sso_url"] = f'{reverse("api:saml2idp:sso_init",args=(app.tenant.uuid,app.id))}'

        return data

    def update(self, app: App, data: Dict) -> Dict:  # pylint: disable=arguments-differ
        """
        更新APP
        """
        try:
            idp_init(app.tenant.uuid, app.id)
        except Exception as err:  # pylint: disable=broad-except
            logger.debug(
                f"idp初始化出错:{err}")  # pylint: disable=logging-fstring-interpolation
            idpclear(app.tenant.uuid, app.id)
            raise err

        data["idp_metadata"] = get_app_config().get_host() + \
            reverse("api:saml2idp:download_metadata",
                    args=(app.tenant.uuid, app.id))

        filename = f"{app.tenant.uuid}_{app.id}"
        filename = BASEDIR + '/djangosaml2idp/saml2_config/%s.xml' % filename
        xmldata = data.get('xmldata', '')
        entity_id = data.get('entity_id', '')
        cert = data.get('cert', "")
        acs = data.get('acs', "")
        sls = data.get('sls', "")

        xmldata_file = data.get("xmldata_file", None)
        if xmldata_file not in ["", None]:
            xmldata_file = xmldata_file.replace("data:text/xml;base64,", "")
            data["xmldata"] = base64.b64decode(xmldata_file)
            data["xmldata"] = data["xmldata"].decode()

        if xmldata not in ['', None]:
            with open(filename, 'w') as f:
                f.write(xmldata)
        else:
            self.dump_cert(filename, cert)
            try:
                self.gen_xml(filename=filename,
                             entity_id=entity_id, acs=acs, sls=sls)
            except CertificateError:
                raise Exception({'msg': 'perm incorrect'}
                                )  # pylint: disable=raise-missing-from

        try:
            sp_metadatafile = MetaDataFile(attrc=None, filename=filename)
            sp_metadatafile.load()
            sp_entity = sp_metadatafile.entity[list(sp_metadatafile.keys())[0]]

            if entity_id in ["", None]:
                data["entity_id"] = sp_entity["entity_id"]

            spsso_descriptor = sp_entity["spsso_descriptor"][0]
            if acs in ["", None]:
                data["acs"] = spsso_descriptor["assertion_consumer_service"][0]["location"]

            try:
                if sls in ["", None]:
                    data["sls"] = spsso_descriptor["single_logout_service"][0]["location"]
            except Exception as err:
                print(err)
                pass

            if cert in ["", None]:
                data["cert"] = spsso_descriptor["key_descriptor"][0]["key_info"]["x509_data"][0]["x509_certificate"]["text"]

        except Exception as err:  # pylint: disable=broad-except
            print(err)
            raise Exception({'msg': '元数据文件解析出错'}
                            )  # pylint: disable=raise-missing-from

        if os.path.exists(BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename):
            os.remove(
                BASEDIR + '/djangosaml2idp/saml2_config/sp_cert/%s.pem' % filename)

        app.url = f'{reverse("api:saml2idp:saml_sso_hook",args=(app.tenant.uuid,app.id))}?spauthn='+'{token}'
        if data.get("sso_url", None) in ["", None]:
            data["sso_url"] = f'{reverse("api:saml2idp:sso_init",args=(app.tenant.uuid,app.id))}'
        return data

    def delete(self):
        """
        删除APP
        """
        print(self)
        return super().delete()

    def dump_cert(self, filename, cert) -> None:
        """
        写入sp验证文件
        """

    def gen_xml(self, filename, entity_id, acs, sls) -> None:
        """
        生成sp元文件
        """
