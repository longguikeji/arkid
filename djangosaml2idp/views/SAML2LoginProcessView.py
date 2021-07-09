"""
SAML2.0协议登陆流程
"""

import logging
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from saml2 import BINDING_HTTP_POST

from djangosaml2idp.utils import repr_saml, verify_request_signature, build_authn_response
from djangosaml2idp.mxins import IdPHandlerViewMixin, LoginRequiredMixin
from djangosaml2idp.idp import IDP
from .SAML2IDPErrorView import SAML2IDPError as error_cbv

logger = logging.getLogger(__name__)


@method_decorator(never_cache, name='dispatch')
class LoginProcess(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View which processes the actual SAML request and returns a self-submitting form with the SAML response.
        The login_required decorator ensures the user authenticates first on the IdP using 'normal' ways.
    """

    def get(self, request, tenant__uuid, app_id):
        """SAML2.0协议登陆流程
        """
        binding = request.session.get('Binding', BINDING_HTTP_POST)

        # TODO: would it be better to store SAML info in request objects?
        # AuthBackend takes request obj as argument...
        try:
            idp_server = IDP.load(tenant__uuid, app_id)

            # Parse incoming request
            req_info = idp_server.parse_authn_request(
                request.session['SAMLRequest'], 
                binding
            )

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

            authn_resp = build_authn_response(
                tenant__uuid, request.user, self.get_authn(), resp_args, service_provider)
        except Exception as e:
            return error_cbv.handle_error(request, exception=e, status_code=500)

        html_response = self.create_html_response(
            request,
            binding=resp_args['binding'],
            authn_resp=authn_resp,
            destination=resp_args['destination'],
            relay_state=request.session['RelayState'])

        logger.debug(
            "--- SAML Authn Response [\n{}] ---".format(repr_saml(str(authn_resp))))
        return self.render_response(request, html_response, processor)
