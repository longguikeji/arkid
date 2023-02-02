"""
IdPHandlerViewMixin
"""
import base64
import copy
import logging
from django.http import HttpRequest
from django.utils.module_loading import import_string
from saml2.server import Server
from saml2.config import IdPConfig
from ..idp import BaseProcessor
from ..idp import idpsettings
from ..views.idp.SAML2IDPErrorView import SAML2IDPError as error_cbv
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from arkid.core.models import TenantExtensionConfig
logger = logging.getLogger(__name__)


class IdPHandlerViewMixin:
    """ Contains some methods used by multiple views """

    def handle_error(self, request, **kwargs):    # pylint: disable=missing-function-docstring
        return error_cbv.as_view()(request, **kwargs)

    def dispatch(self, request, tenant_id, config_id, *args, **kwargs):
        """
        Construct IDP server with config from settings dict
        """
        self.config = TenantExtensionConfig.active_objects.get(id=config_id)
        conf = IdPConfig()
        try:

            conf.load(
                copy.copy(
                    idpsettings.get_saml_idp_config(
                        tenant_id, 
                        config_id,
                        self.config.config["namespace"]
                    )
                )
            )
            self.IDP = Server(config=conf)    # pylint: disable=invalid-name
        except Exception as e:    # pylint: disable=invalid-name, broad-except
            return self.handle_error(request, exception=e)
        return super(IdPHandlerViewMixin, self).dispatch(request, tenant_id, config_id, *args, **kwargs)

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
                pass
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
    
    def create_html_response(self, request: HttpRequest, binding, authn_resp, destination, relay_state):
        """ Login form for SSO
        """

        http_args = self.IDP.apply_binding(
            binding=binding,
            msg_str=authn_resp,
            destination=destination,
            relay_state=relay_state,
            response=True)

        # logger.debug('http args are: %s' % http_args)
        # html_response = {
        #     "data": http_args['headers'][0][1],
        #     "type": "REDIRECT",
        # }
        return http_args