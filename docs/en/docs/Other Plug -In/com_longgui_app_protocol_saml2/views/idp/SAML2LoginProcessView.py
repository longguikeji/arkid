"""
SAML2.0协议登陆流程
"""
import logging
from django.http import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.cache import never_cache
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from saml2 import BINDING_HTTP_POST,BINDING_HTTP_REDIRECT
from saml2.authn_context import PASSWORD, AuthnBroker, authn_context_class_ref
from saml2.ident import NameID
from saml2.md import entity_descriptor_from_string
from saml2.s_utils import UnknownPrincipal, UnsupportedBinding
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED

from ...idp.processors import BaseProcessor
from ...mxins import LoginRequiredMixin, IdPHandlerViewMixin
from ...common.idp.utils import repr_saml, verify_request_signature
logger = logging.getLogger(__name__)


def check_access(processor: BaseProcessor, request: HttpRequest) -> None:
    """ Check if user has access to the service of this SP. Raises a PermissionDenied exception if not.
    """
    if not processor.has_access(request):
        raise PermissionDenied(_("You do not have access to this resource"))


def get_sp_config(config):
    """ Get a dict with the configuration for a SP according to the SAML_IDP_SPCONFIG settings.
        Raises an exception if no SP matching the given entity id can be found.
    """
    sp_config = {
        'attribute_mapping': {
            'email': 'email',
            'private_email': 'private_email',
            'username': 'username',
            'is_staff': 'is_staff',
            'is_superuser': 'is_superuser',
            'token': 'token',
        },
        'extra_config': config.get("attribute_mapping", {})
    }
    return sp_config


def get_authn(req_info=None):
    req_authn_context = req_info.message.requested_authn_context if req_info else PASSWORD
    broker = AuthnBroker()
    broker.add(authn_context_class_ref(req_authn_context), "")
    return broker.get_authn_by_accr(req_authn_context)


@method_decorator(never_cache, name='dispatch')
class LoginProcess(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View which processes the actual SAML request and returns a self-submitting form with the SAML response.
        The login_required decorator ensures the user authenticates first on the IdP using 'normal' ways.
    """

    def get(self, request, tenant_id, config_id):  # pylint: disable=unused-argument
        """SAML2.0协议登陆流程
        """
        binding = request.session.get('Binding', BINDING_HTTP_POST)
        # Parse incoming request

        req_info = self.IDP.parse_authn_request(
            request.session.get('SAMLRequest', None),
            binding
        )

        # check SAML request signature
        try:
            verify_request_signature(req_info)
        except ValueError as excp:
            return self.handle_error(request, extra_message=excp, status=400)

        # Compile Response Arguments
        resp_args = self.IDP.response_args(req_info.message)
        # Set SP and Processor
        sp_config = get_sp_config(self.config.config)
        # Check if user has access
        try:
            # Check if user has access to SP
            check_access(
                self.get_processor(
                    resp_args['sp_entity_id'],
                    sp_config
                ),
                request
            )
        except PermissionDenied as excp:
            return self.handle_error(request, extra_message=excp, status=400)
        # Construct SamlResponse message
        authn_resp = self.build_authn_response(
            request.user,
            get_authn(),
            resp_args,
            sp_config,
            self.config
        )

        html_response = self.create_html_response(
            request,
            binding=resp_args['binding'],
            authn_resp=authn_resp,
            destination=resp_args['destination'],
            relay_state=request.session['RelayState'])

        logger.debug(
            "--- SAML Authn Response [\n{}] ---".format(repr_saml(str(authn_resp))))
        return self.render_response(request, self.get_processor(resp_args['sp_entity_id'], sp_config), html_response)

    def render_response(self, request, processor, http_args):    # pylint: disable=no-self-use
        """
        Return either as redirect to MultiFactorView or as html with self-submitting form.
        """
        if processor.enable_multifactor(request.user):
            # Store http_args in session for after multi factor is complete
            request.session['saml_data'] = http_args['data']
            logger.debug("Redirecting to process_multi_factor")
            return HttpResponseRedirect(reverse('saml_multi_factor'))
        logger.debug("Performing SAML redirect")
        # return HttpResponseRedirect(http_args['headers'][0][1])
        return HttpResponse(http_args['data'])

    # type: ignore
    def build_authn_response(self, user, authn, resp_args, sp_config, config) -> list:
        """ pysaml2 server.Server.create_authn_response wrapper
        """
        policy = resp_args.get('name_id_policy', None)
        if policy is None:
            name_id_format = NAMEID_FORMAT_UNSPECIFIED
        else:
            name_id_format = policy.format or NAMEID_FORMAT_UNSPECIFIED

        idp_name_id_format_list = self.IDP.config.getattr("name_id_format", "idp") or [
            NAMEID_FORMAT_UNSPECIFIED]

        if name_id_format not in idp_name_id_format_list:
            raise ImproperlyConfigured(
                _('SP requested a name_id_format that is not supported in the IDP: {}').format(name_id_format))

        processor: BaseProcessor = self.get_processor(
            resp_args['sp_entity_id'], 
            sp_config
        )  # type: ignore
        user_id = processor.get_user_id(user)

        if self.config.config.get("type",None)=="Saml2SP_AliyunRam":
                user_id = f"{user_id}@{self.config.config.get('auxiliary_domain')}"
        name_id = NameID(
            format=name_id_format,
            sp_name_qualifier=resp_args["sp_entity_id"], 
            text=user_id
        )
        if config.config.get("sp_xml_data", None):
            _spsso_descriptor = entity_descriptor_from_string(
                config.config["xmldata"]
            ).spsso_descriptor.pop()
            sign_response = getattr(
                _spsso_descriptor,
                'want_response_signed',
                ''
            ) == 'true'
            sign_assertion = getattr(
                _spsso_descriptor,
                'want_assertions_signed',
                ''
            ) == 'true'

        else:
            sign_response = config.config.get("sign_response", True)
            sign_assertion = config.config.get("sign_assertion", True)

        encrypt_saml_responses = config.config.get("encrypt_saml_responses", False)

        return self.IDP.create_authn_response(
            authn=authn,
            identity=processor.create_identity(
                user, sp_config["attribute_mapping"]),
            name_id=name_id,
            userid=user_id,
            # Signing
            sign_response=sign_response,
            sign_assertion=sign_assertion,
            encrypt_assertion=encrypt_saml_responses,
            encrypted_advice_attributes=encrypt_saml_responses,
            **resp_args
        )
