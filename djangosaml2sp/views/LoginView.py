"""
SAML2 SP login
"""
import base64
import logging
import saml2

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as AuthLogoutView
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import (HttpRequest, HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, HttpResponseServerError)
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import urlquote
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.module_loading import import_string
from saml2.client_base import LogoutError
from saml2.config import SPConfig
from saml2.ident import code, decode
from saml2.mdstore import SourceNotFound
from saml2.metadata import entity_descriptor
from saml2.response import (RequestVersionTooLow,
                            SignatureError, StatusAuthnFailed, StatusError,
                            StatusNoAuthnContext, StatusRequestDenied,
                            UnsolicitedResponse)
from saml2.s_utils import UnsupportedBinding
from saml2.saml import SCM_BEARER
from saml2.saml import AuthnContextClassRef
from saml2.samlp import RequestedAuthnContext
from saml2.samlp import AuthnRequest, IDPEntry, IDPList, Scoping
from saml2.sigver import MissingKey
from saml2.validate import ResponseLifetimeExceed, ToEarly

from djangosaml2sp.cache import IdentityCache, OutstandingQueriesCache, StateCache
from djangosaml2sp.conf import get_config
from djangosaml2sp.exceptions import IdPConfigurationMissing
from djangosaml2sp.overrides import Saml2Client
from djangosaml2sp.utils import (add_idp_hinting, available_idps, get_custom_setting,
                    get_fallback_login_redirect_url,
                    get_idp_sso_supported_bindings, get_location,
                    validate_referral_url)

from djangosaml2sp.mxins import SPConfigViewMixin


logger = logging.getLogger('djangosaml2')

def get_namespace_prefixes():
    from saml2 import md, saml, samlp, xmlenc, xmldsig
    return {'saml': saml.NAMESPACE,
            'samlp': samlp.NAMESPACE,
            'md': md.NAMESPACE,
            'ds': xmldsig.NAMESPACE,
            'xenc': xmlenc.NAMESPACE}

class Login(SPConfigViewMixin, View):
    """ SAML Authorization Request initiator.

        This view initiates the SAML2 Authorization handshake
        using the pysaml2 library to create the AuthnRequest.

        post_binding_form_template is a path to a template containing HTML form with
        hidden input elements, used to send the SAML message data when HTTP POST
        binding is being used. You can customize this template to include custom
        branding and/or text explaining the automatic redirection process. Please
        see the example template in templates/djangosaml2/example_post_binding_form.html
        If set to None or nonexistent template, default form from the saml2 library
        will be rendered.
    """

    wayf_template = getattr(
        settings,
        'SAML2_CUSTOM_WAYF_TEMPLATE','djangosaml2/wayf.html'
    )
    authorization_error_template = getattr(
        settings,
        'SAML2_CUSTOM_AUTHORIZATION_ERROR_TEMPLATE',
        'djangosaml2/auth_error.html'
    )
    post_binding_form_template = getattr(
        settings,
        'SAML2_CUSTOM_POST_BINDING_FORM_TEMPLATE',
        'djangosaml2sp/post_binding_form.html'
    )

    def get_next_path(self, request: HttpRequest) -> str:
        ''' Returns the path to put in the RelayState to redirect the user to after having logged in.
            If the user is already logged in (and if allowed), he will redirect to there immediately.
        '''

        next_path = get_fallback_login_redirect_url()
        if 'next' in request.GET:
            next_path = request.GET['next']
        elif 'RelayState' in request.GET:
            next_path = request.GET['RelayState']

        next_path = validate_referral_url(request, next_path)
        return next_path

    def unknown_idp(self, request, idp):
        msg = (f'Error: IdP EntityID {idp} was not found in metadata')
        logger.error(msg)
        return HttpResponse(
            msg.format('Please contact technical support.'), status=403
        )

    def load_sso_kwargs_scoping(self, sso_kwargs):
        """ Performs IdP Scoping if scoping param is present. """
        idp_scoping_param = self.request.GET.get('scoping', None)
        if idp_scoping_param:
            idp_scoping = Scoping()
            idp_scoping.idp_list = IDPList()
            idp_scoping.idp_list.idp_entry.append(
                IDPEntry(provider_id = idp_scoping_param)
            )
            sso_kwargs['scoping'] = idp_scoping

    def load_sso_kwargs_authn_context(self, sso_kwargs):
        # this would work when https://github.com/IdentityPython/pysaml2/pull/807
        ac = getattr(self.conf, '_sp_requested_authn_context', {})

        # this works even without https://github.com/IdentityPython/pysaml2/pull/807
        # hopefully to be removed soon !
        if not ac:
            scs = getattr(
                settings, 'SAML_CONFIG', {}
            ).get('service', {}).get('sp', {})
            ac = scs.get('requested_authn_context', {})
        # end transitional things to be removed soon !

        if ac:
            sso_kwargs["requested_authn_context"] = RequestedAuthnContext(
                    authn_context_class_ref=[
                        AuthnContextClassRef(ref) for ref in ac['authn_context_class_ref']
                    ],
                    comparison=ac.get('comparison', "minimum"),
                )

    def load_sso_kwargs(self, sso_kwargs):
        """ Inherit me if you want to put your desidered things in sso_kwargs """

    def get(self, request,tenant_uuid, *args, **kwargs):
        logger.debug('Login process started')
        next_path = self.get_next_path(request)

        # if the user is already authenticated that maybe because of two reasons:
        # A) He has this URL in two browser windows and in the other one he
        #    has already initiated the authenticated session.
        # B) He comes from a view that (incorrectly) send him here because
        #    he does not have enough permissions. That view should have shown
        #    an authorization error in the first place.
        # We can only make one thing here and that is configurable with the
        # SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN setting. If that setting
        # is True (default value) we will redirect him to the next_path path.
        # Otherwise, we will show an (configurable) authorization error.
        if request.user.is_authenticated:
            if get_custom_setting('SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN', True):
                return HttpResponseRedirect(next_path)
            logger.debug('User is already logged in')
            return render(request, self.authorization_error_template, {
                'came_from': next_path,
            })

        try:
            conf = self.get_sp_config(tenant_uuid)
        except SourceNotFound as excp:  # pragma: no cover
            # this is deprecated and it's here only for the doubts that something
            # would happen the day after I'll remove it! :)
            return self.unknown_idp(request, idp='unknown')

        # is a embedded wayf or DiscoveryService needed?
        configured_idps = available_idps(conf)
        selected_idp = request.GET.get('idp', None)

        self.conf = conf
        sso_kwargs = {}

        # Do we have a Discovery Service?
        if not selected_idp:
            discovery_service = getattr(settings, 'SAML2_DISCO_URL', None)
            if discovery_service:
                # We have to build the URL to redirect to with all the information
                # for the Discovery Service to know how to send the flow back to us
                logger.debug(("A discovery process is needed trough a"
                              "Discovery Service: {}").format(discovery_service))
                login_url = request.build_absolute_uri(reverse('saml2_login'))
                login_url = '{0}?next={1}'.format(login_url,
                                                  urlquote(next_path, safe=''))
                ds_url = '{0}?entityID={1}&return={2}&returnIDParam=idp'
                ds_url = ds_url.format(discovery_service,
                                       urlquote(
                                           getattr(conf, 'entityid'), safe=''),
                                       urlquote(login_url, safe=''))
                return HttpResponseRedirect(ds_url)

            elif len(configured_idps) > 1:
                logger.debug('A discovery process trough WAYF page is needed')
                return render(request, self.wayf_template, {
                    'available_idps': configured_idps.items(),
                    'came_from': next_path,
                })

        # is the first one, otherwise next logger message will print None
        if not configured_idps: # pragma: no cover
            raise IdPConfigurationMissing(
                ('IdP is missing or its metadata is expired.'))
        if selected_idp is None:
            selected_idp = list(configured_idps.keys())[0]

        # choose a binding to try first
        binding = getattr(settings, 'SAML_DEFAULT_BINDING',
                          saml2.BINDING_HTTP_POST)
        logger.debug(f'Trying binding {binding} for IDP {selected_idp}')

        # ensure our selected binding is supported by the IDP
        try:
            supported_bindings = get_idp_sso_supported_bindings(
                selected_idp, config=conf)
        except saml2.s_utils.UnknownSystemEntity:
            return self.unknown_idp(request, selected_idp)

        if binding not in supported_bindings:
            logger.debug(
                f'Binding {binding} not in IDP {selected_idp} '
                f'supported bindings: {supported_bindings}. Trying to switch ...',
            )
            if binding == saml2.BINDING_HTTP_POST:
                logger.warning(
                    f'IDP {selected_idp} does not support {binding} '
                    f'trying {saml2.BINDING_HTTP_REDIRECT}',
                )
                binding = saml2.BINDING_HTTP_REDIRECT
            else: # pragma: no cover
                logger.warning(
                    f'IDP {selected_idp} does not support {binding} '
                    f'trying {saml2.BINDING_HTTP_POST}',
                )
                binding = saml2.BINDING_HTTP_POST
            # if switched binding still not supported, give up
            if binding not in supported_bindings: # pragma: no cover
                raise UnsupportedBinding(
                    f'IDP {selected_idp} does not support '
                    f'{saml2.BINDING_HTTP_POST} or {saml2.BINDING_HTTP_REDIRECT}'
                )

        client = Saml2Client(conf)

        # SSO options
        sign_requests = getattr(conf, '_sp_authn_requests_signed', False)
        if sign_requests:
            sso_kwargs["sigalg"] = getattr(conf, '_sp_signing_algorithm',
                                           saml2.xmldsig.SIG_RSA_SHA256
            )
            sso_kwargs["digest_alg"] = getattr(conf,
                                               '_sp_digest_algorithm',
                                               saml2.xmldsig.DIGEST_SHA256
            )
        # pysaml needs a string otherwise: "cannot serialize True (type bool)"
        if getattr(conf, '_sp_force_authn', False):
            sso_kwargs['force_authn'] = "true"
        if getattr(conf, '_sp_allow_create', False):
            sso_kwargs['allow_create'] = "true"

        # custom nsprefixes
        sso_kwargs['nsprefix'] = get_namespace_prefixes()


        # Enrich sso_kwargs ...
        # idp scoping
        self.load_sso_kwargs_scoping(sso_kwargs)
        # authn context
        self.load_sso_kwargs_authn_context(sso_kwargs)
        # other customization to be inherited
        self.load_sso_kwargs(sso_kwargs)

        logger.debug(f'Redirecting user to the IdP via {binding} binding.')
        _msg = 'Unable to know which IdP to use'
        http_response = None

        if binding == saml2.BINDING_HTTP_REDIRECT:
            try:
                session_id, result = client.prepare_for_authenticate(
                    entityid=selected_idp, relay_state=next_path,
                    binding=binding, sign=sign_requests,
                    **sso_kwargs)
            except TypeError as e:
                logger.error(f'{_msg}: {e}')
                return HttpResponse(_msg)
            else:
                http_response = HttpResponseRedirect(get_location(result))

        elif binding == saml2.BINDING_HTTP_POST:
            if self.post_binding_form_template:
                # get request XML to build our own html based on the template
                try:
                    location = client.sso_location(selected_idp, binding)
                except TypeError as e:
                    logger.error(f'{_msg}: {e}')
                    return HttpResponse(_msg)

                session_id, request_xml = client.create_authn_request(
                    location,
                    binding=binding,
                    **sso_kwargs
                )
                try:
                    if isinstance(request_xml, AuthnRequest):
                        # request_xml will be an instance of AuthnRequest if the message is not signed
                        request_xml = str(request_xml)
                    saml_request = base64.b64encode(
                        bytes(request_xml, 'UTF-8')).decode('utf-8')

                    http_response = render(request, self.post_binding_form_template, {
                        'target_url': location,
                        'params': {
                            'SAMLRequest': saml_request,
                            'RelayState': next_path,
                        },
                    })
                except TemplateDoesNotExist as e:
                    logger.debug(
                        f'TemplateDoesNotExist: [{self.post_binding_form_template}] - {e}'
                    )

            if not http_response:
                # use the html provided by pysaml2 if no template was specified or it doesn't exist
                try:
                    session_id, result = client.prepare_for_authenticate(
                        entityid=selected_idp, relay_state=next_path,
                        binding=binding, **sso_kwargs)
                except TypeError as e:
                    _msg = f"Can't prepare the authentication for {selected_idp}"
                    logger.error(f'{_msg}: {e}')
                    return HttpResponse(_msg)
                else:
                    http_response = HttpResponse(result['data'])
        else:
            raise UnsupportedBinding(f'Unsupported binding: {binding}')

        # success, so save the session ID and return our response
        # oq_cache = OutstandingQueriesCache(request.session)
        # oq_cache.set(session_id, next_path)
        # logger.debug(
        #     f'Saving the session_id "{oq_cache.__dict__}" '
        #     'in the OutstandingQueries cache',
        # )

        # idp hinting support, add idphint url parameter if present in this request
        response = add_idp_hinting(request, http_response) or http_response
        return response
