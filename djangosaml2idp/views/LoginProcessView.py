import copy
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from saml2.s_utils import UnknownPrincipal, UnsupportedBinding
from extension_root.saml2idp.provider import BASE_DIR
import os
from django.urls.base import reverse
from extension_root.saml2idp.constants import BASE_URL
from rest_framework.authtoken.models import Token

from saml2 import BINDING_HTTP_POST, NAMEID_FORMAT_EMAILADDRESS,saml,BINDING_HTTP_REDIRECT
from saml2.config import IdPConfig
from saml2.server import Server
from saml2.sigver import get_xmlsec_binary

from django.conf import settings

@method_decorator(never_cache, name='dispatch')
class LoginProcess(View):
    """
    View which processes the actual SAML request and returns a self-submitting form with the SAML response.
    The login_required decorator ensures the user authenticates first on the IdP using 'normal' ways.
    """

    def cookie_user(self, request):    # pylint: disable=no-self-use
        '''返回cookie对应的用户
        '''
        try:
            spauthn = request.COOKIES['spauthn']
            token = Token.objects.get(key=spauthn)
            return token.user
        except Exception:    # pylint: disable=broad-except
            return request.user
    def get_SAML_IDP_CONFIG(self,tenant_uuid,app_id):
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
                    'name_id_format': [NAMEID_FORMAT_EMAILADDRESS, saml.NAMEID_FORMAT_UNSPECIFIED],
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
        return SAML_IDP_CONFIG

    def get_IDP_Server(self,SAML_IDP_CONFIG):
        conf = IdPConfig()
        conf.load(copy.copy(SAML_IDP_CONFIG))
        return Server(config=conf)

    def get(self, request, tenant_uuid, app_id, *args, **kwargs):    # pylint: disable=missing-function-docstring, unused-argument, too-many-locals
        binding = request.session.get('Binding', BINDING_HTTP_POST)
        SAML_IDP_CONFIG = self.get_SAML_IDP_CONFIG(tenant_uuid,app_id)
        self.IDP = self.get_IDP_Server(SAML_IDP_CONFIG)
        # Parse incoming request
        try:
            req_info = self.IDP.parse_authn_request(
                request.session['SAMLRequest'], binding)
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp)
        # Signed request for HTTP-REDIRECT
        if "SigAlg" in request.session and "Signature" in request.session:
            _certs = self.IDP.metadata.certs(
                req_info.message.issuer.text, "any", "signing")
            verified_ok = False
            for cert in _certs:    # pylint: disable=unused-variable
                # TODO implement
                # if verify_redirect_signature(_info, self.IDP.sec.sec_backend, cert):
                #    verified_ok = True
                #    break
                pass
            if not verified_ok:
                return self.handle_error(request, extra_message="Message signature verification failure", status=400)
        # Gather response arguments
        try:
            resp_args = self.IDP.response_args(req_info.message)
        except (UnknownPrincipal, UnsupportedBinding) as excp:
            return self.handle_error(request, exception=excp, status=400)
        # print('resp_args is', resp_args)
        try:
            # sp_config = SAML_IDP_SPCONFIG[resp_args['sp_entity_id']]
            sp_config = {
                'processor': 'djangosaml2idp.processors.BaseProcessor',
                'attribute_mapping': {
                    'email': 'email',
                    'private_email': 'private_email',
                    'username': 'username',
                    'is_staff': 'is_staff',
                    'is_superuser': 'is_superuser',
                    'token': 'token',
                },
            }
        except Exception:    # pylint: disable=broad-except
            return self.handle_error(request,
                                     exception=ImproperlyConfigured("No config for SP %s defined in SAML_IDP_SPCONFIG" %
                                                                    resp_args['sp_entity_id']),
                                     status=400)
        processor = self.get_processor(resp_args['sp_entity_id'], sp_config)

        # Check if user has access to the service of this SP
        if not processor.has_access(request):
            return self.handle_error(request,
                                     exception=PermissionDenied(
                                         "You do not have access to this resource"),
                                     status=403)
        cookie_user = self.cookie_user(request)
        identity = self.get_identity(processor, cookie_user, sp_config)
        req_authn_context = req_info.message.requested_authn_context or PASSWORD
        # print('cookie_user is', cookie_user)
        # print('identity is', identity)
        # print('req_authn_context is', req_authn_context)
        AUTHN_BROKER = AuthnBroker()    # pylint: disable=invalid-name
        AUTHN_BROKER.add(authn_context_class_ref(req_authn_context), "")
        user_id = processor.get_user_id(cookie_user)
        # Construct SamlResponse message
        try:
            app = SAMLAPP.valid_objects.get(
                entity_id=resp_args['sp_entity_id'])
            _spsso_descriptor = entity_descriptor_from_string(
                app.xmldata).spsso_descriptor.pop()    # pylint: disable=no-member
            authn_resp = self.IDP.create_authn_response(
                identity=identity,
                userid=user_id,
                # name_id=NameID(format=resp_args['name_id_policy'].format,
                #                sp_name_qualifier=resp_args['sp_entity_id'],
                #                text=user_id),
                name_id=NameID(format=resp_args['name_id_policy'],
                               sp_name_qualifier=resp_args['sp_entity_id'],
                               text=user_id),
                authn=AUTHN_BROKER.get_authn_by_accr(req_authn_context),
                sign_response=getattr(
                    _spsso_descriptor, 'want_response_signed', '') == 'true',
                sign_assertion=getattr(
                    _spsso_descriptor, 'want_assertions_signed', '') == 'true',
                **resp_args)
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)
        # print('authn_resp is', authn_resp)
        http_args = self.IDP.apply_binding(binding=resp_args['binding'],
                                           msg_str="%s" % authn_resp,
                                           destination=resp_args['destination'],
                                           relay_state=request.session['RelayState'],
                                           response=True)

        logger.debug('http args are: %s' %
                     http_args)    # pylint: disable=logging-not-lazy
        return self.render_response(request, processor, http_args)

    def render_response(self, request, processor, http_args):    # pylint: disable=no-self-use
        """
        Return either as redirect to MultiFactorView or as html with self-submitting form.
        """
        if processor.enable_multifactor(self.cookie_user(request)):
            # Store http_args in session for after multi factor is complete
            request.session['saml_data'] = http_args['data']
            logger.debug("Redirecting to process_multi_factor")
            return HttpResponseRedirect(reverse('saml_multi_factor'))
        logger.debug("Performing SAML redirect")
        # return HttpResponseRedirect(http_args['headers'][0][1])
        return HttpResponse(http_args['data'])

