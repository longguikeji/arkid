import json
import logging
import urllib
import urllib.parse as urlparse
from datetime import timedelta
from urllib.parse import urlencode
import importlib

from Cryptodome.PublicKey import RSA
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from jwkest import long_to_base64
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View
from django.conf import settings
from drf_expiring_authtoken.models import ExpiringToken
from ..exceptions import OAuthToolkitError
from ..forms import AllowForm
from ..http import OAuth2ResponseRedirect
from ..models import get_access_token_model, get_oidc_access_token_model, get_application_model, get_oidc_application_model, get_oidc_rsa_key_model
from ..scopes import get_scopes_backend
from ..settings import oauth2_settings
from ..signals import app_authorized
from ..backends import OAuth2Backend
from .mixins import OAuthLibMixin
from oauth2_provider.models import OidcAccessToken
from oneid_meta.models import APP

log = logging.getLogger("oauth2_provider")


from django.contrib.auth.mixins import AccessMixin
from rest_framework.exceptions import AuthenticationFailed
from drf_expiring_authtoken.authentication import ExpiringTokenAuthentication

ONEID_TOKEN_KEY = 'oneid_token'


class TokenRequiredMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        scope = (request.GET.get('scope', '').strip("\n")).split(' ')
        client_id = request.GET.get('client_id', '').strip("\n")
        if 'openid' in scope:
            app = APP.valid_objects.filter(oidc_app__client_id=client_id).first()
        else:
            app = APP.valid_objects.filter(oauth_app__client_id=client_id).first()
        if not app:
            return HttpResponse("Can't find app, please contact your IT manager")

        is_authenticated = self.check_token(request, None if app.allow_any_user else app.default_perm)
        if is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

    def check_token(self, request, required_perm):
        '''
        此token指OneID内部自身登录状态与身份证明的标识
        '''
        token = request.GET.get(ONEID_TOKEN_KEY, '')
        request.META['HTTP_AUTHORIZATION'] = 'Token ' + token
        try:
            res = ExpiringTokenAuthentication().authenticate(request)
            if res is not None:
                user, _ = res
                if not user.has_perm_realtime(required_perm):
                    return False
                request.user = user
                return True
            return False
        except AuthenticationFailed:
            return False

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return self._redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    def _redirect_to_login(self, next_url, login_url, redirect_field_name):
        '''
        preserve fragment after #
        '''

        # TODO
        from django.shortcuts import resolve_url
        from urllib.parse import urlparse, urlunparse
        from django.http import QueryDict

        resolved_url = resolve_url(login_url or settings.LOGIN_URL)
        login_url_parts = list(urlparse(resolved_url))
        # scheme='', netloc='', path='/_/', params='', query='', fragment='/oneid/login'
        # -> 
        # scheme='', netloc='', path='/_/#/oneid/login', params='', query='', fragment=''
        login_url_parts[2] += '#{}'.format(login_url_parts[5])
        login_url_parts[5] = ''
        if redirect_field_name:
            querystring = QueryDict(login_url_parts[4], mutable=True)
            querystring[redirect_field_name] = next_url
            login_url_parts[4] = querystring.urlencode(safe='/')
        return HttpResponseRedirect(urlunparse(login_url_parts))


class BaseAuthorizationView(TokenRequiredMixin, OAuthLibMixin, View):
    """
    Implements a generic endpoint to handle *Authorization Requests* as in :rfc:`4.1.1`. The view
    does not implement any strategy to determine *authorize/do not authorize* logic.
    The endpoint is used in the following flows:

    * Authorization code
    * Implicit grant

    """
    def dispatch(self, request, *args, **kwargs):
        self.oauth2_data = {}
        self.extra_data = {}
        return super().dispatch(request, *args, **kwargs)

    def error_response(self, error, application, **kwargs):
        """
        Handle errors either by redirecting to redirect_uri with a json in the body containing
        error details or providing an error response
        """
        redirect, error_response = super().error_response(error, **kwargs)
        if redirect:
            return self.redirect(error_response["url"], application)

        status = error_response["error"].status_code
        return self.render_to_response(error_response, status=status)

    def redirect(self, redirect_to, application):
        if application is None:
            # The application can be None in case of an error during app validation
            # In such cases, fall back to default ALLOWED_REDIRECT_URI_SCHEMES
            allowed_schemes = oauth2_settings.ALLOWED_REDIRECT_URI_SCHEMES
        else:
            allowed_schemes = application.get_allowed_schemes()
        return OAuth2ResponseRedirect(redirect_to, allowed_schemes)


class AuthorizationWraperView(View):

    def get(self, request):
        '''
        get token from FE and then redirect to AuthorizationView
        '''
        url_path = request.get_full_path()
        if ONEID_TOKEN_KEY in request.GET:
            token = request.GET.get(ONEID_TOKEN_KEY)
            print('get token, go to auth', token)
            url_path = url_path.replace('authorize', '_authorize', 1)
            return HttpResponseRedirect(url_path)
        else:
            fe_token_url = settings.FE_TOKEN_URL
            target = urllib.parse.quote(url_path)
            print('miss token, go to fe', fe_token_url)
            print('target', target)
            return HttpResponseRedirect(fe_token_url + '?target={}'.format(target))

class AuthorizationView(BaseAuthorizationView, FormView):
    """
    Implements an endpoint to handle *Authorization Requests* as in :rfc:`4.1.1` and prompting the
    user with a form to determine if she authorizes the client application to access her data.
    This endpoint is reached two times during the authorization process:
    * first receive a ``GET`` request from user asking authorization for a certain client
    application, a form is served possibly showing some useful info and prompting for
    *authorize/do not authorize*.

    * then receive a ``POST`` request possibly after user authorized the access

    Some informations contained in the ``GET`` request and needed to create a Grant token during
    the ``POST`` request would be lost between the two steps above, so they are temporarily stored in
    hidden fields on the form.
    A possible alternative could be keeping such informations in the session.

    The endpoint is used in the following flows:
    * Authorization code
    * Implicit grant
    """
    template_name = "oauth2_provider/authorize.html"
    form_class = AllowForm

    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS
    oidclib_backend = 'oauth2_provider.oauth2_backends'

    skip_authorization_completely = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_initial(self):
        # TODO: move this scopes conversion from and to string into a utils function
        scopes = self.oauth2_data.get("scope", self.oauth2_data.get("scopes", []))
        initial_data = {
            "redirect_uri": self.oauth2_data.get("redirect_uri", None),
            "scope": " ".join(scopes),
            "client_id": self.oauth2_data.get("client_id", None),
            "state": self.oauth2_data.get("state", None),
            "response_type": self.oauth2_data.get("response_type", None),
            "next_path": self.extra_data.get("next_path", None),
            "nonce": self.oauth2_data.get("nonce", None),
            "code_challenge": self.oauth2_data.get("code_challenge", None),
            "code_challenge_method": self.oauth2_data.get("code_challenge_method", None),
        }
        return initial_data

    def form_valid(self, form):
        client_id = form.cleaned_data["client_id"]
        scopes = form.cleaned_data.get("scope").split(' ')
        if 'openid' in scopes:
            application = get_oidc_application_model().objects.get(client_id=client_id)
        else:
            application = get_application_model().objects.get(client_id=client_id)
        credentials = {
            "client_id": form.cleaned_data.get("client_id"),
            "redirect_uri": form.cleaned_data.get("redirect_uri"),
            "response_type": form.cleaned_data.get("response_type", None),
            "state": form.cleaned_data.get("state", None),
            "nonce": form.cleaned_data.get("nonce", None),
            "code_challenge": form.cleaned_data.get("code_challenge", None),
            "code_challenge_method": form.cleaned_data.get("code_challenge_method", None),
        }
        for key in [
            "code_challenge",
            "code_challenge_method",
        ]:
            if credentials[key] == "":
                credentials[key] = None
        scopes = form.cleaned_data.get("scope")
        next_path = form.cleaned_data.get("next_path")
        allow = form.cleaned_data.get("allow")

        try:
            uri, headers, body, status = self.create_authorization_response(  # oauth2_provider/views/mixins.py -> oauthlib\oauth2\rfc6749\endpoints\authorization.py -> oauthlib.oauth2.rfc6749.grant_types.implicit.ImplicitGrant -> ...
                request=self.request, scopes=scopes, credentials=credentials, allow=allow
            )
            if 'openid' in scopes.split(' ') and application.response_type != 'code':
                oneid_token = ExpiringToken.objects.get(key=self.request.META.get('HTTP_AUTHORIZATION').split(' ')[1])
                queryset = OidcAccessToken.objects.filter(token=oneid_token.key)
                if queryset:
                    access_token = queryset[0]
                    access_token.expires = timezone.now() + timedelta(
                        seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
                else:
                    access_token = OidcAccessToken.objects.create(
                        token=oneid_token.key,
                        application=application,
                        expires=timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                    )
                id_token = self.validator_class().create_id_token(access_token, oneid_token.user, client_id, nonce='',
                                                                  at_hash=access_token.at_hash, request=None, scope=None)
                access_token.scope = scopes
                access_token.source_refresh_token = None
                access_token.id_token = id_token
                access_token.save()
                id_token = get_oidc_access_token_model().encode_id_token(access_token.id_token, access_token.application)
                uri = self.validator_class().refactor_oidc_authorization_uri(application.response_type,
                                                                             access_token.token,
                                                                             id_token, uri)
        except OAuthToolkitError as error:
            return self.error_response(error, application)

        if next_path:
            uri = self.add_param_to_url(uri, {'next_path': next_path})
        self.success_url = uri

        log.debug("Success url for the request: {0}".format(self.success_url))
        return self.redirect(self.success_url, application)

    @staticmethod
    def add_param_to_url(url, params):
        '''
        :param str url:
        :param dict params:
        '''
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)

    def get(self, request, *args, **kwargs):
        try:
            scopes, credentials = self.validate_authorization_request(request)
        except OAuthToolkitError as error:
            # Application is not available at this time.
            return self.error_response(error, application=None)

        all_scopes = get_scopes_backend().get_all_scopes()
        kwargs["scopes_descriptions"] = [all_scopes[scope] for scope in scopes]
        kwargs["scopes"] = scopes
        # at this point we know an Application instance with such client_id exists in the database
        # TODO: Cache this!
        application = get_oidc_application_model().objects.get(client_id=credentials["client_id"]) if 'openid' in scopes \
            else get_application_model().objects.get(client_id=credentials["client_id"])
        kwargs["application"] = application
        kwargs["client_id"] = credentials["client_id"]
        kwargs["redirect_uri"] = credentials["redirect_uri"]
        kwargs["response_type"] = credentials["response_type"]
        kwargs["state"] = credentials["state"]
        kwargs["nonce"] = credentials.get('nonce', '')
        kwargs["code_challenge"] = credentials.get('code_challenge', '')
        kwargs["code_challenge_method"] = credentials.get('code_challenge_method', '')

        self.oauth2_data = kwargs
        next_path = ''
        for key in oauth2_settings.LOGIN_NEXT_PARAM_NAMES:
            value = request.GET.get(key)
            if value:
                next_path = value
        self.extra_data = {
            'next_path': next_path,
        }

        # following two loc are here only because of https://code.djangoproject.com/ticket/17795
        form = self.get_form(self.get_form_class())
        kwargs["form"] = form

        # Check to see if the user has already granted access and return
        # a successful response depending on "approval_prompt" url parameter
        require_approval = request.GET.get("approval_prompt", oauth2_settings.REQUEST_APPROVAL_PROMPT)

        try:
            # If skip_authorization field is True, skip the authorization screen even
            # if this is the first use of the application and there was no previous authorization.
            # This is useful for in-house applications-> assume an in-house applications
            # are already approved.
            if application.skip_authorization:
                uri, headers, body, status = self.create_authorization_response(
                    request=self.request, scopes=" ".join(scopes),
                    credentials=credentials, allow=True
                )
                return self.redirect(uri, application)

            elif require_approval == "auto":
                tokens = get_access_token_model().objects.filter(
                    user=request.user,
                    application=kwargs["application"],
                    expires__gt=timezone.now()
                ).all()

                # check past authorizations regarded the same scopes as the current one
                for token in tokens:
                    if token.allow_scopes(scopes):
                        uri, headers, body, status = self.create_authorization_response(
                            request=self.request, scopes=" ".join(scopes),
                            credentials=credentials, allow=True
                        )
                        return self.redirect(uri, application)
        except OAuthToolkitError as error:
            return self.error_response(error, application)
        return self.render_to_response(self.get_context_data(**kwargs))


@method_decorator(csrf_exempt, name="dispatch")
class TokenView(OAuthLibMixin, View):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_token_response(request)
        if status == 200:
            json_body = json.loads(body)
            access_token = json_body.get("access_token")
            if access_token is not None:
                access_token_model = get_access_token_model() if 'openid' not in json_body.get("scope") else get_oidc_access_token_model()
                token = access_token_model.objects.get(token=access_token)
                oneid_token, _ = ExpiringToken.objects.get_or_create(user=token.user)
                for duplicate_token in access_token_model.objects.filter(token=oneid_token.key):
                    duplicate_token.delete()
                token.token = oneid_token.key
                token.save()
                app_authorized.send(
                    sender=self, request=request,
                    token=token)
                dic_body = json_body
                dic_body['access_token'] = oneid_token.key
                if 'openid' in json_body.get("scope"):
                    dic_body['id_token'] = get_oidc_access_token_model().encode_id_token(token.id_token, token.application)
                body = json.dumps(dic_body)
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response


@method_decorator(csrf_exempt, name="dispatch")
class RevokeTokenView(OAuthLibMixin, View):
    """
    Implements an endpoint to revoke access or refresh tokens
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_revocation_response(request)
        response = HttpResponse(content=body or "", status=status)

        for k, v in headers.items():
            response[k] = v
        return response


class UserInfoOauthView(APIView):
    authentication_classes = [OAuth2Backend]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        response = Response({
            "data": {
                "user": {
                    "id": user.id,
                    "name": user.username,
                    "email": user.email,
                },
            },
        })

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        return response


class UserInfoOidcView(APIView):
    authentication_classes = [OAuth2Backend]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        response = Response({
            "sub": user.id,
            'preferred_username': user.username,
            "email": user.email,
        })

        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "*"
        response["Access-Control-Allow-Credentials"] = "true"
        return response


class JwksView(APIView):

    def get(self, request, *args, **kwargs):
        dic = dict(keys=[])

        for rsakey in get_oidc_rsa_key_model().objects.all():
            public_key = RSA.importKey(rsakey.key).publickey()
            dic['keys'].append({
                'kty': 'RSA',
                'alg': 'RS256',
                'use': 'sig',
                'kid': rsakey.kid,
                'n': long_to_base64(public_key.n),
                'e': long_to_base64(public_key.e),
            })

        response = JsonResponse(dic)
        response['Access-Control-Allow-Origin'] = '*'
        return response


class OidcProviderInfoView(View):

    validator_module = 'oauth2_provider.oauth2_validators'

    def get(self, request, *args, **kwargs):
        dic = dict()

        validator_module = importlib.import_module(self.validator_module)
        site_url = validator_module.get_site_url(request=request)
        dic['issuer'] = validator_module.get_issuer(site_url=site_url, request=request)
        dic['scopes_supported'] = [key for key in oauth2_settings.SCOPES.keys()]
        dic['authorization_endpoint'] = site_url + reverse('oauth2_provider:authorize_wraper')
        dic['token_endpoint'] = site_url + reverse('oauth2_provider:token')
        dic['userinfo_endpoint'] = site_url + reverse('oauth2_provider:userinfo')
        # dic['end_session_endpoint'] = site_url + reverse('oauth2_provider:end-session')
        dic['introspection_endpoint'] = site_url + reverse('oauth2_provider:oidc_introspect')
        dic['response_types_supported'] = [response_type[0] for response_type in get_oidc_application_model().RESPONSE_TYPES]
        dic['jwks_uri'] = site_url + reverse('oauth2_provider:jwks')
        dic['id_token_signing_alg_values_supported'] = [jwt_alg[0] for jwt_alg in get_oidc_application_model().JWT_ALGS]
        # See: http://openid.net/specs/openid-connect-core-1_0.html#SubjectIDTypes
        dic['subject_types_supported'] = [client_type[0] for client_type in get_oidc_application_model().CLIENT_TYPES]
        dic['token_endpoint_auth_methods_supported'] = ['client_secret_post', 'client_secret_basic']

        # if settings.get('OIDC_SESSION_MANAGEMENT_ENABLE'):
        #     dic['check_session_iframe'] = site_url + reverse('oidc_provider:check-session-iframe')

        response = JsonResponse(dic)
        response['Access-Control-Allow-Origin'] = '*'

        return response
