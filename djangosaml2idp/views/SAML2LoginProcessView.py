import logging
from django.core.exceptions import ImproperlyConfigured
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext as _

from saml2 import BINDING_HTTP_POST
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED, NameID
from saml2.authn_context import PASSWORD, AuthnBroker, authn_context_class_ref

from djangosaml2idp.utils import repr_saml, verify_request_signature
from djangosaml2idp.mxins import IdPHandlerViewMixin, LoginRequiredMixin
from djangosaml2idp.idp import IDP
from .SAML2IDPErrorView import SAML2IDPError as error_cbv

logger = logging.getLogger(__name__)

@method_decorator(never_cache, name='dispatch')
class LoginProcessView(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View which processes the actual SAML request and returns a self-submitting form with the SAML response.
        The login_required decorator ensures the user authenticates first on the IdP using 'normal' ways.
    """

    def get(self, request, tenant__uuid, *args, **kwargs):
        binding = request.session.get('Binding', BINDING_HTTP_POST)

        # TODO: would it be better to store SAML info in request objects?
        # AuthBackend takes request obj as argument...
        try:
            idp_server = IDP.load(tenant__uuid)

            # Parse incoming request
            req_info = idp_server.parse_authn_request(request.session['SAMLRequest'], binding)

            # check SAML request signature
            try:
                verify_request_signature(req_info)
            except ValueError as excp:
                return error_cbv.handle_error(request, exception=excp, status_code=400)

            # Compile Response Arguments
            resp_args = idp_server.response_args(req_info.message)
            # Set SP and Processor

            sp_entity_id = resp_args.pop('sp_entity_id')
            service_provider = get_sp_config(sp_entity_id)
                        
            # TODO 权限验证 
            # # Check if user has access
            # try:
            #     # Check if user has access to SP
            #     check_access(service_provider.processor, request)
            # except PermissionDenied as excp:
            #     return error_cbv.handle_error(request, exception=excp, status_code=403)
            # Construct SamlResponse message

            authn_resp = self.build_authn_response(tenant__uuid, request.user, self.get_authn(), resp_args, service_provider)
        except Exception as e:
            return error_cbv.handle_error(request, exception=e, status_code=500)

        html_response = self.create_html_response(
            request,
            binding=resp_args['binding'],
            authn_resp=authn_resp,
            destination=resp_args['destination'],
            relay_state=request.session['RelayState'])

        logger.debug("--- SAML Authn Response [\n{}] ---".format(repr_saml(str(authn_resp))))
        return self.render_response(request, html_response, processor)

    def build_authn_response(self, tenant__uuid,user: User, authn, resp_args, service_provider: ServiceProvider) -> list:  # type: ignore
        """ pysaml2 server.Server.create_authn_response wrapper
        """
        policy = resp_args.get('name_id_policy', None)
        if policy is None:
            name_id_format = NAMEID_FORMAT_UNSPECIFIED
        else:
            name_id_format = policy.format

        idp_server = IDP.load(tenant__uuid)
        idp_name_id_format_list = idp_server.config.getattr("name_id_format", "idp") or [NAMEID_FORMAT_UNSPECIFIED]

        if name_id_format not in idp_name_id_format_list:
            raise ImproperlyConfigured(_('SP requested a name_id_format that is not supported in the IDP: {}').format(name_id_format))

        processor: BaseProcessor = service_provider.processor  # type: ignore
        user_id = processor.get_user_id(user, name_id_format, service_provider, idp_server.config)
        name_id = NameID(format=name_id_format, sp_name_qualifier=service_provider.entity_id, text=user_id)

        return idp_server.create_authn_response(
            authn=authn,
            identity=processor.create_identity(user, service_provider.attribute_mapping),
            name_id=name_id,
            userid=user_id,
            sp_entity_id=service_provider.entity_id,
            # Signing
            sign_response=service_provider.sign_response,
            sign_assertion=service_provider.sign_assertion,
            sign_alg=service_provider.signing_algorithm,
            digest_alg=service_provider.digest_algorithm,
            # Encryption
            encrypt_assertion=service_provider.encrypt_saml_responses,
            encrypted_advice_attributes=service_provider.encrypt_saml_responses,
            **resp_args
        )
    def get_authn(self, req_info=None):
        req_authn_context = req_info.message.requested_authn_context if req_info else PASSWORD
        broker = AuthnBroker()
        broker.add(authn_context_class_ref(req_authn_context), "")
        return broker.get_authn_by_accr(req_authn_context)