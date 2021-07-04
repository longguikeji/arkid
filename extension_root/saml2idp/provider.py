import os
from typing import Dict

from django.conf import settings
from saml2.sigver import get_xmlsec_binary
from app.models import App
from common.provider import AppTypeProvider
from django.urls import reverse
from djangosaml2.cert import check_or_create_self_signed_cert
import copy
from six import text_type

from .constants import BASE_URL

from saml2.config import IdPConfig
from saml2.metadata import entity_descriptor
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class SAML2IDPAppTypeProvider(AppTypeProvider):

    def create(self, app: App, data: Dict) -> Dict:
        self.gem_url(app)

        # 处理SSL证书
        cert_base_dir = os.path.join(
            BASE_DIR,
            f"certificates/{app.tenant.uuid}/{app.id}/"
        )
        check_or_create_self_signed_cert(cert_base_dir)

        # 处理metadata
        self.create_metadata(app.tenant.uuid, app.id)
        data["metadata_file_path"] = os.path.join(
            BASE_DIR,
            f"saml2_config/{app.tenant.uuid}/{app.id}/idp_metadata.xml"
        )

        data["BASE_DIR"] = BASE_DIR

        return data

    def update(self, app: App, data: Dict) -> Dict:
        self.gem_url(app)

        # 处理SSL证书
        cert_base_dir = os.path.join(
            BASE_DIR,
            f"certificates/{app.tenant.uuid}/{app.id}/"
        )
        check_or_create_self_signed_cert(cert_base_dir)
        # 处理metadata
        self.create_metadata(app.tenant.uuid, app.id)
        data["metadata_file_path"] = os.path.join(
            BASE_DIR,
            f"saml2_config/{app.tenant.uuid}/{app.id}/idp_metadata.xml"
        )

        data["BASE_DIR"] = BASE_DIR

        return data

    def gem_url(self, app: App):
        """
        自动生成APP地址
        """
        url = reverse("api:saml2idp:dev_index", args=[app.tenant.uuid, app.id])
        app.url = url

    def create_metadata(self, tenant_uuid, app_id):
        """
        创建metadata文件
        :param tenant_uuid 租户ID
        :param app_id 应用ID 
        """
        # 判断是否已经创建了metadata
        metadata_dir = os.path.join(
            BASE_DIR,
            f"saml2_config/{tenant_uuid}/{app_id}/"
        )
        if not os.path.exists(metadata_dir):
            os.makedirs(metadata_dir)

        metadata_file_path = os.path.join(metadata_dir, "idp_metadata.xml")
        if os.path.exists(metadata_file_path):
            return

        # config
        SAML_IDP_CONFIG = {
            'debug': settings.DEBUG,
            'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
            'entityid': f'{BASE_URL}{reverse("api:saml2idp:metadata", args=[tenant_uuid,app_id])}',
            'description': 'longguikeji IdP setup',
            'service': {
                'idp': {
                    'name': 'Django localhost IdP',
                    'endpoints': {
                        'single_sign_on_service': [
                            (f'{BASE_URL}{reverse("api:saml2idp:login_post", args=[tenant_uuid,app_id])}', BINDING_HTTP_POST),
                            (f'{BASE_URL}{reverse("api:saml2idp:login_redirect", args=[tenant_uuid,app_id])}', BINDING_HTTP_REDIRECT),
                        ],
                    },
                    'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED],
                    'sign_response': False,
                    'sign_assertion': False,
                },
            },
            'metadata': {
                'local': [
                    os.path.join(
                        os.path.join(
                            BASE_DIR,
                            f"saml2_config/{tenant_uuid}/{app_id}/"
                        ),
                        f
                    ) for f in os.listdir(
                        os.path.join(
                            BASE_DIR,
                            f"saml2_config/{tenant_uuid}/{app_id}/"
                        )
                    ) if f.split('.')[-1] == 'xml'
                ],
            },
            # Signing
            'key_file': os.path.join(BASE_DIR, f"certificates/{tenant_uuid}/{app_id}/key.pem"),
            'cert_file': os.path.join(BASE_DIR, f"certificates/{tenant_uuid}/{app_id}/cert.pem"),
            # Encryption
            'encryption_keypairs': [{
                'key_file': os.path.join(BASE_DIR, f"certificates/{tenant_uuid}/{app_id}/key.pem"),
                'cert_file': os.path.join(BASE_DIR, f"certificates/{tenant_uuid}/{app_id}/cert.pem"),
            }],
            'valid_for': 365 * 24,
        }

        conf = IdPConfig()    # pylint: disable=invalid-name
        conf.load(copy.deepcopy(SAML_IDP_CONFIG))

        meta_data = entity_descriptor(conf)    # pylint: disable=invalid-name
        content = text_type(meta_data).encode('utf-8')

        with open(metadata_file_path, 'wb') as f:
            f.write(content)
