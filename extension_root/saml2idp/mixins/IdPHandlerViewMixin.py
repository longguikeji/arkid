import os
from django.conf import settings
from django.utils.module_loading import import_string
from .. import idpsettings

from saml2.saml import NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED
from saml2.sigver import get_xmlsec_binary
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT, saml
from saml2.authn_context import PASSWORD, AuthnBroker, authn_context_class_ref
from saml2.config import IdPConfig
from saml2.ident import NameID
from saml2.metadata import entity_descriptor
from saml2.s_utils import UnknownPrincipal, UnsupportedBinding
from saml2.server import Server
from saml2.md import entity_descriptor_from_string

logger = logging.getLogger(__name__)    # pylint: disable=invalid-name

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class IdPHandlerViewMixin:
    """ Contains some methods used by multiple views """

    error_view = import_string(
        getattr(idpsettings, 'SAML_IDP_ERROR_VIEW_CLASS', 'djangosaml2idp.error_views.SamlIDPErrorView'))

    def handle_error(self, request, **kwargs):    # pylint: disable=missing-function-docstring
        return self.error_view.as_view()(request, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        """
        Construct IDP server with config from settings dict
        """
        conf = IdPConfig()
        try:
            SAML_IDP_CONFIG = {  # pylint: disable=invalid-name
                'debug': settings.DEBUG,
                'xmlsec_binary': get_xmlsec_binary(['/opt/local/bin', '/usr/bin/xmlsec1']),
                'entityid': '%s/saml/metadata/' % settings.BASE_URL,
                'description': 'longguikeji IdP setup',

                'service': {
                    'idp': {
                        'name': 'Django localhost IdP',
                        'endpoints': {
                            'single_sign_on_service': [
                                ('%s/saml/sso/post/' %
                                 settings.BASE_URL, BINDING_HTTP_POST),
                                ('%s/saml/sso/redirect/' %
                                 settings.BASE_URL, BINDING_HTTP_REDIRECT),
                            ],
                        },
                        'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, NAMEID_FORMAT_UNSPECIFIED],
                        'sign_response': True,
                        'sign_assertion': True,
                    },
                },

                'metadata': {
                    'local': [os.path.join(os.path.join(os.path.join(BASEDIR, 'djangosaml2idp'), \
                                                        'saml2_config'), f) for f in
                              os.listdir(BASEDIR + '/djangosaml2idp/saml2_config/') \
                              if f.split('.')[-1] == 'xml'],
                },
                # Signing
                'key_file': BASEDIR + '/djangosaml2idp/certificates/mykey.pem',
                'cert_file': BASEDIR + '/djangosaml2idp/certificates/mycert.pem',
                # Encryption
                'encryption_keypairs': [{
                    'key_file': BASEDIR + '/djangosaml2idp/certificates/mykey.pem',
                    'cert_file': BASEDIR + '/djangosaml2idp/certificates/mycert.pem',
                }],
                'valid_for': 365 * 24,
            }

            conf.load(copy.copy(SAML_IDP_CONFIG))
            self.IDP = Server(config=conf)    # pylint: disable=invalid-name
        except Exception as e:    # pylint: disable=invalid-name, broad-except
            return self.handle_error(request, exception=e)
        return super(IdPHandlerViewMixin, self).dispatch(request, *args, **kwargs)

    def get_processor(self, entity_id, sp_config):    # pylint: disable=no-self-use
        """
        Instantiate user-specified processor or default to an all-access base processor.
        Raises an exception if the configured processor class can not be found or initialized.
        """
        processor_string = sp_config.get('processor', None)
        if processor_string:
            try:
                return import_string(processor_string)(entity_id)
            except Exception as e:    # pylint: disable=invalid-name
                logger.error("Failed to instantiate processor: {} - {}".format(processor_string,
                             e), exc_info=True)    # pylint: disable=logging-format-interpolation
                raise
        return BaseProcessor(entity_id)

    def get_identity(self, processor, user, sp_config):    # pylint: disable=no-self-use
        """
        Create Identity dict (using SP-specific mapping)
        """
        sp_mapping = sp_config.get('attribute_mapping', {
                                   'username': 'username'})
        ret = processor.create_identity(
            user, sp_mapping, **sp_config.get('extra_config', {}))
        return ret
