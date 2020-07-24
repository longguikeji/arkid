'''
django SAML views
'''
import os
import logging
import copy
from socket import gethostname
from OpenSSL import crypto

from django.conf import settings
from django.db import transaction
from django.shortcuts import reverse
from django.contrib.auth import logout, REDIRECT_FIELD_NAME
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseRedirect)
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from six import text_type
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

from djangosaml2idp.serializers.aliyun import AliyunSSORoleSerializer
from djangosaml2idp.processors import BaseProcessor
from djangosaml2idp import idpsettings
from oneid.permissions import IsAdminUser, IsUserManager
from oneid_meta.models import SAMLAPP, AliyunSSORole
from drf_expiring_authtoken.models import ExpiringToken

logger = logging.getLogger(__name__)    # pylint: disable=invalid-name

BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# pylint: disable=too-many-lines
def create_self_signed_cert():
    '''
    生成自签名证书存放于相对路径下
    '''
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    cert = crypto.X509()
    cert.get_subject().C = "CN"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    with open(BASEDIR + '/djangosaml2idp/certificates/mycert.pem', "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(BASEDIR + "/djangosaml2idp/certificates/mykey.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


@never_cache
@csrf_exempt
@require_http_methods(["GET", "POST"])
def sso_entry(request):
    """ Entrypoint view for SSO. Gathers the parameters from the HTTP request, stores them in the session
        and redirects the requester to the login_process view.
    """
    if request.method == 'POST':
        passed_data = request.POST
        binding = BINDING_HTTP_POST
    else:
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT

    request.session['Binding'] = binding
    try:
        request.session['SAMLRequest'] = passed_data['SAMLRequest']
    except (KeyError, MultiValueDictKeyError) as e:    # pylint: disable=invalid-name
        return HttpResponseBadRequest(e)
    request.session['RelayState'] = passed_data.get('RelayState', '')
    # TODO check how the redirect saml way works. Taken from example idp in pysaml2.
    if "SigAlg" in passed_data and "Signature" in passed_data:
        request.session['SigAlg'] = passed_data['SigAlg']
        request.session['Signature'] = passed_data['Signature']
    return HttpResponseRedirect(reverse('djangosaml2idp:saml_login_process'))


class AccessMixin:
    """
    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = None
    permission_denied_message = ''
    raise_exception = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_login_url(self):
        """
        Override this method to override the login_url attribute.
        """
        login_url = self.login_url or settings.SAML_LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__))
        return str(login_url)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message

    def get_redirect_field_name(self):
        """
        Override this method to override the redirect_field_name attribute.
        """
        return self.redirect_field_name

    def handle_no_permission(self, request_data):
        '''
        未登录用户跳转登录页面
        '''
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return HttpResponseRedirect(settings.SAML_LOGIN_URL + '?SAMLRequest={}'.format(request_data))


class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""
    def dispatch(self, request, *args, **kwargs):
        '''检查用户cookies是否登录
        '''
        try:
            spauthn = request.COOKIES['spauthn']
            token = ExpiringToken.objects.get(key=spauthn)
            exp = token.expired()
            if not exp:
                return super().dispatch(request, *args, **kwargs)
        except Exception:    # pylint: disable=broad-except
            return self.handle_no_permission(request.session['SAMLRequest'])


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
                                ('%s/saml/sso/post/' % settings.BASE_URL, BINDING_HTTP_POST),
                                ('%s/saml/sso/redirect/' % settings.BASE_URL, BINDING_HTTP_REDIRECT),
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
                logger.error("Failed to instantiate processor: {} - {}".format(processor_string, e), exc_info=True)    # pylint: disable=logging-format-interpolation
                raise
        return BaseProcessor(entity_id)

    def get_identity(self, processor, user, sp_config):    # pylint: disable=no-self-use
        """
        Create Identity dict (using SP-specific mapping)
        """
        sp_mapping = sp_config.get('attribute_mapping', {'username': 'username'})
        ret = processor.create_identity(user, sp_mapping, **sp_config.get('extra_config', {}))
        return ret


@method_decorator(never_cache, name='dispatch')
class LoginProcessView(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """
    View which processes the actual SAML request and returns a self-submitting form with the SAML response.
    The login_required decorator ensures the user authenticates first on the IdP using 'normal' ways.
    """
    def cookie_user(self, request):    # pylint: disable=no-self-use
        '''返回cookie对应的用户
        '''
        try:
            spauthn = request.COOKIES['spauthn']
            token = ExpiringToken.objects.get(key=spauthn)
            return token.user
        except Exception:    # pylint: disable=broad-except
            return request.user

    def get(self, request, *args, **kwargs):    # pylint: disable=missing-function-docstring, unused-argument, too-many-locals
        binding = request.session.get('Binding', BINDING_HTTP_POST)
        # Parse incoming request
        try:
            req_info = self.IDP.parse_authn_request(request.session['SAMLRequest'], binding)
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp)
        # Signed request for HTTP-REDIRECT
        if "SigAlg" in request.session and "Signature" in request.session:
            _certs = self.IDP.metadata.certs(req_info.message.issuer.text, "any", "signing")
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
                                     exception=PermissionDenied("You do not have access to this resource"),
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
            app = SAMLAPP.valid_objects.get(entity_id=resp_args['sp_entity_id'])
            _spsso_descriptor = entity_descriptor_from_string(app.xmldata).spsso_descriptor.pop()    # pylint: disable=no-member
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
                sign_response=getattr(_spsso_descriptor, 'want_response_signed', '') == 'true',
                sign_assertion=getattr(_spsso_descriptor, 'want_assertions_signed', '') == 'true',
                **resp_args)
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)
        # print('authn_resp is', authn_resp)
        http_args = self.IDP.apply_binding(binding=resp_args['binding'],
                                           msg_str="%s" % authn_resp,
                                           destination=resp_args['destination'],
                                           relay_state=request.session['RelayState'],
                                           response=True)

        logger.debug('http args are: %s' % http_args)    # pylint: disable=logging-not-lazy
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


@method_decorator(never_cache, name='dispatch')    # pylint: disable=missing-class-docstring
class SSOInitView(LoginRequiredMixin, IdPHandlerViewMixin, View):
    def post(self, request, *args, **kwargs):    # pylint: disable=missing-function-docstring
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):    # pylint: disable=missing-function-docstring, too-many-locals, unused-argument
        passed_data = request.POST if request.method == 'POST' else request.GET

        # get sp information from the parameters
        try:
            sp_entity_id = passed_data['sp']
        except KeyError as excp:
            return self.handle_error(request, exception=excp, status=400)

        try:
            # sp_config = SAML_IDP_SPCONFIG[sp_entity_id]
            sp_config = {
                'processor': 'djangosaml2idp.processors.BaseProcessor',
                'attribute_mapping': {
                    'username': 'username',
                    'email': 'email',
                    'name': 'first_name',
                    'is_boss': 'is_admin',
                    'token': 'token',
                }
            }
        except Exception:    # pylint: disable=broad-except
            return self.handle_error(request,
                                     exception=ImproperlyConfigured("No config for SP %s defined in SAML_IDP_SPCONFIG" %
                                                                    sp_entity_id),
                                     status=400)

        binding_out, destination = self.IDP.pick_binding(service="assertion_consumer_service", entity_id=sp_entity_id)

        processor = self.get_processor(sp_entity_id, sp_config)

        # Check if user has access to the service of this SP
        if not processor.has_access(request):
            return self.handle_error(request,
                                     exception=PermissionDenied("You do not have access to this resource"),
                                     status=403)

        identity = self.get_identity(processor, request.user, sp_config)

        req_authn_context = PASSWORD
        AUTHN_BROKER = AuthnBroker()    # pylint: disable=invalid-name
        AUTHN_BROKER.add(authn_context_class_ref(req_authn_context), "")

        user_id = processor.get_user_id(request.user)

        # Construct SamlResponse messages
        try:
            name_id_formats = self.IDP.config.getattr("name_id_format", "idp") or [NAMEID_FORMAT_UNSPECIFIED]
            name_id = NameID(format=name_id_formats[0], text=user_id)
            authn = AUTHN_BROKER.get_authn_by_accr(req_authn_context)
            sign_response = self.IDP.config.getattr("sign_response", "idp") or False
            sign_assertion = self.IDP.config.getattr("sign_assertion", "idp") or False
            authn_resp = self.IDP.create_authn_response(identity=identity,
                                                        in_response_to=None,
                                                        destination=destination,
                                                        sp_entity_id=sp_entity_id,
                                                        userid=user_id,
                                                        name_id=name_id,
                                                        authn=authn,
                                                        sign_response=sign_response,
                                                        sign_assertion=sign_assertion,
                                                        **passed_data)
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)

        # Return as html with self-submitting form.
        http_args = self.IDP.apply_binding(binding=binding_out,
                                           msg_str="%s" % authn_resp,
                                           destination=destination,
                                           relay_state=passed_data['RelayState'],
                                           response=True)
        return HttpResponse(http_args['data'])


@method_decorator(never_cache, name='dispatch')
class ProcessMultiFactorView(LoginRequiredMixin, View):
    """
    This view is used in an optional step is to perform 'other' user validation, for example 2nd factor checks.
    Override this view per the documentation if using this functionality to plug in your custom validation logic.
    """
    def multifactor_is_valid(self, request):    # pylint: disable=no-self-use, unused-argument
        """ The code here can do whatever it needs to validate your user (via request.user or elsewise).
            It must return True for authentication to be considered a success.
        """
        return True

    def get(self, request, *args, **kwargs):    # pylint: disable=unused-argument, missing-function-docstring
        if self.multifactor_is_valid(request):
            logger.debug('MultiFactor succeeded for %s' % request.user)    # pylint: disable=logging-not-lazy
            # If authentication succeeded, log in is ok
            return HttpResponse(request.session['saml_data'])
        logger.debug("MultiFactor failed; %s will not be able to log in" % request.user)    # pylint: disable=logging-not-lazy
        logout(request)
        raise PermissionDenied("MultiFactor authentication factor failed")


@never_cache
def metadata(request):    # pylint: disable=unused-argument
    """
    Returns an XML with the SAML 2.0 metadata for this Idp.
    The metadata is constructed on-the-fly based on the config dict in the django settings.
    """
    conf = IdPConfig()
    conf.load(idpsettings.SAML_IDP_CONFIG)
    meta_data = entity_descriptor(conf)
    return HttpResponse(content=text_type(meta_data).encode('utf-8'), content_type="text/xml; charset=utf8")


@never_cache
def download_metadata(request):    # pylint: disable=unused-argument
    """
    Returns an XML with the SAML 2.0 metadata for this Idp.
    The metadata is constructed on-the-fly based on the config dict in the django settings.
    """
    res = metadata(request)
    res['Content-Type'] = 'application/octet-stream'
    res['Content-Disposition'] = 'attachment;filename="idp_metadata.xml"'
    return res


class SuccessURLAllowedHostsMixin:    # pylint: disable=missing-class-docstring
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):    # pylint: disable=missing-function-docstring

        allowed_hosts = {self.request.get_host()}
        allowed_hosts.update(self.success_url_allowed_hosts)
        return allowed_hosts


class AliyunRoleSSOAccessMixin(AccessMixin):
    """
    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = settings.ALIYUN_ROLE_SSO_LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        """检查用户cookies是否登录"""
        try:
            spauthn = request.COOKIES['spauthn']
            token = ExpiringToken.objects.get(key=spauthn)
            exp = token.expired()
            if not exp:
                return super().dispatch(request, *args, **kwargs)
        except Exception:    # pylint: disable=broad-except
            return self.handle_no_permission()

    def handle_no_permission(self, request_data=None):
        """未登录用户跳转登录页面"""
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return HttpResponseRedirect(settings.ALIYUN_ROLE_SSO_LOGIN_URL)


@method_decorator(never_cache, name='dispatch')
class AliyunSSORoleView(AliyunRoleSSOAccessMixin, IdPHandlerViewMixin, View):
    """
    阿里云角色SSO登录
    """

    SP_ENTITY_ID = 'urn:alibaba:cloudcomputing'
    IN_RESPONSE_TO = 'https://signin.aliyun.com/saml-role/sso'
    DESTINATION = 'https://signin.aliyun.com/saml-role/sso'
    CUSTOM_CONFIG = {
        'role': 'https://www.aliyun.com/SAML-Role/Attributes/Role',
        'role_session_name': 'https://www.aliyun.com/SAML-Role/Attributes/RoleSessionName',
        'session_duration': 'https://www.aliyun.com/SAML-Role/Attributes/SessionDuration',
    }

    def cookie_user(self, request):    # pylint: disable=no-self-use
        """
        返回cookie对应的用户
        """
        try:
            spauthn = request.COOKIES['spauthn']
            token = ExpiringToken.objects.get(key=spauthn)
            return token.user
        except Exception:    # pylint: disable=broad-except
            return request.user

    def get(self, request, *args, **kwargs):    # pylint: disable=missing-function-docstring, unused-argument, too-many-locals
        resp_args = {
            'in_response_to': self.IN_RESPONSE_TO,
            'sp_entity_id': self.SP_ENTITY_ID,
            'name_id_policy': saml.NAMEID_FORMAT_PERSISTENT,
            'binding': BINDING_HTTP_POST,
            'destination': self.DESTINATION,
        }
        sp_config = {
            'processor': 'djangosaml2idp.processors.BaseProcessor',
            'attribute_mapping': {
                'username': 'username',
                'token': 'token',
                'aliyun_sso_roles': self.CUSTOM_CONFIG['role'],
                'display_name': self.CUSTOM_CONFIG['role_session_name'],
                'aliyun_sso_session_duration': self.CUSTOM_CONFIG['session_duration'],
            },
        }
        processor = self.get_processor(resp_args['sp_entity_id'], sp_config)
        # Check if user has access to the service of this SP
        if not processor.has_access(request):
            return self.handle_error(request,
                                     exception=PermissionDenied("You do not have access to this resource"),
                                     status=403)
        cookie_user = self.cookie_user(request)
        if not cookie_user.aliyun_sso_role.is_active:
            # 用户的角色SSO被禁用
            return self.handle_error(request, exception=PermissionDenied("Your role SSO has been disabled"), status=403)
        identity = self.get_identity(processor, cookie_user, sp_config)
        # print('identity is', identity)
        AUTHN_BROKER = AuthnBroker()    # pylint: disable=invalid-name
        AUTHN_BROKER.add(authn_context_class_ref(PASSWORD), "")
        user_id = processor.get_user_id(cookie_user)
        # Construct SamlResponse message
        try:
            app = SAMLAPP.valid_objects.get(entity_id=resp_args['sp_entity_id'])
            _spsso_descriptor = entity_descriptor_from_string(app.xmldata).spsso_descriptor.pop()    # pylint: disable=no-member
            authn_resp = self.IDP.create_authn_response(identity=identity,
                                                        userid=user_id,
                                                        name_id=NameID(format=resp_args['name_id_policy'],
                                                                       sp_name_qualifier=resp_args['sp_entity_id'],
                                                                       text=user_id),
                                                        authn=AUTHN_BROKER.get_authn_by_accr(PASSWORD),
                                                        sign_response=getattr(_spsso_descriptor, 'want_response_signed',
                                                                              '') == 'true',
                                                        sign_assertion=getattr(_spsso_descriptor,
                                                                               'want_assertions_signed', '') == 'true',
                                                        **resp_args)
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)
        # print('authn_resp is', authn_resp)
        http_args = self.IDP.apply_binding(binding=resp_args['binding'],
                                           msg_str="%s" % authn_resp,
                                           destination=resp_args['destination'],
                                           response=True)
        return HttpResponse(http_args['data'])


class AliyunSSORoleListCreateAPIView(generics.ListCreateAPIView):
    """用户关联阿里云SSO关联信息"""
    serializer_class = AliyunSSORoleSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser | IsUserManager)]

    def get_queryset(self):
        """return queryset for list [GET]"""
        queryset = AliyunSSORole.valid_objects.all()
        return queryset

    @transaction.atomic()
    def create(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        create aliyun sso role [POST]
        """
        data = request.data
        user_ids = data.get('user_ids', [])
        role_info = {
            'role': data.get('role', []),
            'session_duration': data.get('session_duration', 900),
            'user_id': None
        }
        for user_id in user_ids:
            role_info.update(user_id=user_id)
            serializer = AliyunSSORoleSerializer(data=role_info)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        queryset = AliyunSSORole.valid_objects.filter(user_id__in=user_ids)
        serializer = AliyunSSORoleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AliyunSSORoleDetailCreateAPIView(generics.RetrieveUpdateAPIView):
    """特定阿里云角色SSO信息 [GET],[PATCH]"""
    serializer_class = AliyunSSORoleSerializer
    permission_classes = [IsAuthenticated & (IsAdminUser | IsUserManager)]

    def get_object(self):
        """
        find aliyun role sso
        :rtype: oneid_meta.models.AliyunSSORole
        """
        role = AliyunSSORole.valid_objects.filter(user__username=self.kwargs['username']).first()
        if not role:
            raise NotFound
        # try:
        #     self.check_object_permissions(self.request, user)
        # except PermissionDenied:
        #     raise NotFound
        return role

    def update(self, request, *args, **kwargs):    # pylint: disable=unused-argument
        """
        update aliyun role sso detail [PATCH]
        """
        role = self.get_object()
        data = request.data
        serializer = AliyunSSORoleSerializer(role, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
