
"""
SAML2协议 ServiceProvider
"""
from saml2 import xmldsig
from djangosaml2idp.idp import IDP
import json
from typing import Dict
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from app.models import App
from djangosaml2idp.utils import extract_validuntil_from_metadata

User = get_user_model()

DEFAULT_PROCESSOR = 'djangosaml2idp.processors.BaseProcessor'

DEFAULT_ATTRIBUTE_MAPPING = {
    # DJANGO: SAML
    'email': 'email',
    'private_email': 'private_email',
    'username': 'username',
    'is_staff': 'is_staff',
    'is_superuser': 'is_superuser',
    'token': 'token',
}


class ServiceProvider():
    """
    SAML2.0 协议SP
    """

    def __init__(self, app_id) -> None:
        """
        初始化sp
        :param app_id 应用ID
        """
        self.app = App.active_objects.get(id=app_id)
        self.entity_id = self.app.data.get("entity_id")
        self.local_metadata = self.app.data.get("xmldata")
        try:
            self.metadata_expiration_dt = extract_validuntil_from_metadata(
                self.local_metadata)
        except ValidationError as err:
            print(err)
            self.metadata_expiration_dt = None

        if hasattr(settings, 'SAML_IDP_SP_FIELD_DEFAULT_PROCESSOR'):
            self._processor = getattr(
                settings,
                'SAML_IDP_SP_FIELD_DEFAULT_PROCESSOR'
            )
        else:
            self._processor = DEFAULT_PROCESSOR

        if hasattr(settings, 'SAML_IDP_SP_FIELD_DEFAULT_ATTRIBUTE_MAPPING'):
            self._attribute_mapping = json.dumps(
                getattr(settings, 'SAML_IDP_SP_FIELD_DEFAULT_ATTRIBUTE_MAPPING'))
        else:
            self._attribute_mapping = json.dumps(DEFAULT_ATTRIBUTE_MAPPING)

        self._encrypt_saml_responses = self.app.data.get("_encrypt_saml_responses", None)
        self._sign_response = self.app.data.get("_sign_response", None)
        self._sign_assertion = self.app.data.get("_sign_assertion", None)
        self._nameid_field = self.app.data.get("nameid_field", None)
        self._signing_algorithm = self.app.data.get("_signing_algorithm", None)
        self._digest_algorithm = self.app.data.get("_digest_algorithm", None)

    @property
    def processor(self) -> "BaseProcessor":  # type: ignore
        """
        获取processor
        """
        from djangosaml2idp.processors import validate_processor_path, instantiate_processor
        processor_cls = validate_processor_path(self._processor)
        return instantiate_processor(processor_cls, self.entity_id)

    @property
    def nameid_field(self) -> str:
        """
        """
        if self._nameid_field:
            return self._nameid_field
        if hasattr(settings, 'SAML_IDP_DJANGO_USERNAME_FIELD'):
            return settings.SAML_IDP_DJANGO_USERNAME_FIELD
        return getattr(User, 'USERNAME_FIELD', 'username')

    @property
    def attribute_mapping(self) -> Dict[str, str]:
        if not self._attribute_mapping:
            return DEFAULT_ATTRIBUTE_MAPPING
        return json.loads(self._attribute_mapping)

    @property
    def encrypt_saml_responses(self) -> bool:
        if self._encrypt_saml_responses is None:
            return getattr(settings, 'SAML_ENCRYPT_AUTHN_RESPONSE', False)
        return self._encrypt_saml_responses
        
    @property
    def sign_response(self) -> bool:
        if self._sign_response is None:
            return getattr(IDP.load(self.app.tenant.uuid,self.app.id).config, "sign_response", False)
        return self._sign_response

    @property
    def sign_assertion(self) -> bool:
        if self._sign_assertion is None:
            return getattr(IDP.load(self.app.tenant.uuid,self.app.id).config, "sign_assertion", False)
        return self._sign_assertion

    @property
    def signing_algorithm(self) -> str:
        if self._signing_algorithm is None:
            return getattr(settings, "SAML_AUTHN_SIGN_ALG", xmldsig.SIG_RSA_SHA256)
        return self._signing_algorithm

    @property
    def digest_algorithm(self) -> str:
        if self._digest_algorithm is None:
            return getattr(settings, "SAML_AUTHN_DIGEST_ALG", xmldsig.DIGEST_SHA256)
        return self._digest_algorithm

    @property
    def resulting_config(self) -> str:
        """ Actual values of the config / properties with the settings and defaults taken into account.
        """
        try:
            d = {
                'entity_id': self.entity_id,
                'attribute_mapping': self.attribute_mapping,
                'nameid_field': self.nameid_field,
                'sign_response': self.sign_response,
                'sign_assertion': self.sign_assertion,
                'encrypt_saml_responses': self.encrypt_saml_responses,
                'signing_algorithm': self.signing_algorithm,
                'digest_algorithm': self.digest_algorithm,
            }
            config_as_str = json.dumps(d, indent=4)
        except Exception as e:
            config_as_str = f'Could not render config: {e}'
        # Some ugly replacements to have the json decently printed in the admin
        return mark_safe(config_as_str.replace("\n", "<br>").replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;"))
