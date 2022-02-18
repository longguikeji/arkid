import re
import json
import logging
from tenant.models import Tenant
import urllib.parse

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.template import Template
from  django.template import RequestContext
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, View
from rest_framework.authtoken.models import Token

from ..exceptions import OAuthToolkitError
from ..forms import AllowForm
from ..http import OAuth2ResponseRedirect
from ..models import get_access_token_model, get_application_model
from django.contrib.auth.mixins import AccessMixin
from ..scopes import get_scopes_backend
from ..settings import oauth2_settings
from ..signals import app_authorized
from .mixins import OAuthLibMixin
from config import get_app_config
from arkid.settings import LOGIN_URL
from inventory.models import Permission
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication


log = logging.getLogger("oauth2_provider")


class TokenRequiredMixin(AccessMixin):

    def get_login_url(self):
        full_path = self.request.get_full_path()
        next_uri = urllib.parse.quote(full_path)
        
        # # 地址加租户uuid参数
        uuid_re = r"[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}"
        path = self.request.path
        res = re.search(uuid_re, path)
        if res:
            tenant_uuid = res.group(0)
            tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
            if tenant and tenant.slug:
                redirect_url = '{}{}?next={}'.format(get_app_config().get_slug_frontend_host(tenant.slug), LOGIN_URL, next_uri)
            else:
                redirect_url = '{}{}?tenant={}&next={}'.format(get_app_config().get_frontend_host(), LOGIN_URL, tenant_uuid, next_uri)
        else:
            host = get_app_config().get_host().split('://')[-1]
            request_host = self.request.get_host().split(':')[0]
            slug = request_host.replace('.' + host, '')
            tenant = Tenant.objects.filter(slug=slug).first()
            if tenant and tenant.slug:
                redirect_url = '{}{}?next={}'.format(get_app_config().get_slug_frontend_host(tenant.slug), LOGIN_URL, next_uri)
            else: 
                redirect_url = '{}{}?slug=null&next={}'.format(get_app_config().get_frontend_host(), LOGIN_URL, next_uri)
        return redirect_url

    def dispatch(self, request, *args, **kwargs):
        is_authenticated = self.check_token(request, *args, **kwargs)
        if is_authenticated:
            # 用户
            user = request.user
            # 租户
            tenant = user.tenant
            if not user.check_permission(tenant) is None:
                # 是否有用户权限
                Permission.active_objects.filter(
                    is_system_permission=False,
                    tenant=tenant,
                )
                # 是否有组权限
                pass
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()

    def check_token(self, request, *args, **kwargs):
        token = request.GET.get('token', '')
        request.META['HTTP_AUTHORIZATION'] = 'Token ' + token

        tenant = None
        tenant_uuid = kwargs.get('tenant_uuid')
        if tenant_uuid:
            tenant = Tenant.objects.get(uuid=tenant_uuid)

        if not tenant:
            uuid_re = r"[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}"
            path = self.request.path
            res = re.search(uuid_re, path)
            if res:
                tenant_uuid = res.group(0)
                tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        
        if not tenant:
            host = get_app_config().get_host().split('://')[-1]
            request_host = request.get_host().split(':')[0]
            slug = request_host.replace('.' + host, '')
            tenant = Tenant.objects.filter(slug=slug).first()

        try:
            res = ExpiringTokenAuthentication().authenticate(request)
            if res is not None:
                user, _ = res
                assert tenant is not None
                user.tenant = tenant
                request.user = user
                return True
            return False
        except AuthenticationFailed:
            return False

    def handle_no_permission(self):
        return self._redirect_to_login()

    def _redirect_to_login(self):
        return HttpResponseRedirect(self.get_login_url())


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
        # 即将绑定的用户
        key_obj = Token.objects.filter(user=self.request.user).first()
        if key_obj:
            token = key_obj.key
            redirect_to = "{}&token={}".format(redirect_to, token)
        return OAuth2ResponseRedirect(redirect_to, allowed_schemes)


RFC3339 = "%Y-%m-%dT%H:%M:%SZ"


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

    skip_authorization_completely = False

    def get_initial(self):
        # TODO: move this scopes conversion from and to string into a utils function
        scopes = self.oauth2_data.get("scope", self.oauth2_data.get("scopes", []))
        initial_data = {
            "redirect_uri": self.oauth2_data.get("redirect_uri", None),
            "scope": " ".join(scopes),
            "nonce": self.oauth2_data.get("nonce", None),
            "client_id": self.oauth2_data.get("client_id", None),
            "state": self.oauth2_data.get("state", None),
            "response_type": self.oauth2_data.get("response_type", None),
            "code_challenge": self.oauth2_data.get("code_challenge", None),
            "code_challenge_method": self.oauth2_data.get("code_challenge_method", None),
            "claims": self.oauth2_data.get("claims", None),
        }
        return initial_data

    def form_valid(self, form):
        client_id = form.cleaned_data["client_id"]
        application = get_application_model().objects.get(client_id=client_id)
        credentials = {
            "client_id": form.cleaned_data.get("client_id"),
            "redirect_uri": form.cleaned_data.get("redirect_uri"),
            "response_type": form.cleaned_data.get("response_type", None),
            "state": form.cleaned_data.get("state", None),
        }
        if form.cleaned_data.get("code_challenge", False):
            credentials["code_challenge"] = form.cleaned_data.get("code_challenge")
        if form.cleaned_data.get("code_challenge_method", False):
            credentials["code_challenge_method"] = form.cleaned_data.get("code_challenge_method")
        if form.cleaned_data.get("nonce", False):
            credentials["nonce"] = form.cleaned_data.get("nonce")
        if form.cleaned_data.get("claims", False):
            credentials["claims"] = form.cleaned_data.get("claims")

        scopes = form.cleaned_data.get("scope")
        allow = form.cleaned_data.get("allow")

        try:
            uri, headers, body, status = self.create_authorization_response(
                request=self.request, scopes=scopes, credentials=credentials, allow=allow
            )
        except OAuthToolkitError as error:
            return self.error_response(error, application)

        self.success_url = uri
        log.debug("Success url for the request: {0}".format(self.success_url))
        return self.redirect(self.success_url, application)

    def post(self, request, *args, **kwargs):
        if 'credentials' in request.session and request.session['credentials']:
            credentials = request.session.get("credentials")
            scopes = " ".join(request.session.get("scopes", []))
            allow = True if "allow" in request.POST else False

            client_id = credentials.get("client_id")
            application = get_application_model().objects.get(client_id=client_id)
            try:
                uri, headers, body, status = self.create_authorization_response(
                    request=self.request, scopes=scopes, credentials=credentials, allow=allow
                )
            except OAuthToolkitError as error:
                return self.error_response(error, application)

            self.success_url = uri
            log.debug("Success url for the request: {0}".format(self.success_url))
            request.session.pop('credentials')
            request.session.pop('scopes')
            return self.redirect(self.success_url, application)
        else:
            return super().post(request, *args, **kwargs)

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
        application = get_application_model().objects.get(client_id=credentials["client_id"])
        kwargs["application"] = application
        kwargs["client_id"] = credentials["client_id"]
        kwargs["redirect_uri"] = credentials["redirect_uri"]
        kwargs["response_type"] = credentials["response_type"]
        kwargs["state"] = credentials["state"]
        if "code_challenge" in credentials:
            kwargs["code_challenge"] = credentials["code_challenge"]
        if "code_challenge_method" in credentials:
            kwargs["code_challenge_method"] = credentials["code_challenge_method"]
        if "nonce" in credentials:
            kwargs["nonce"] = credentials["nonce"]
        if "claims" in credentials:
            kwargs["claims"] = json.dumps(credentials["claims"])

        self.oauth2_data = kwargs
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
                    request=self.request, scopes=" ".join(scopes), credentials=credentials, allow=True
                )
                return self.redirect(uri, application)

            elif require_approval == "auto":
                tokens = (
                    get_access_token_model()
                    .objects.filter(
                        user=request.user, application=kwargs["application"], expires__gt=timezone.now()
                    )
                    .all()
                )

                # check past authorizations regarded the same scopes as the current one
                for token in tokens:
                    if token.allow_scopes(scopes):
                        uri, headers, body, status = self.create_authorization_response(
                            request=self.request,
                            scopes=" ".join(scopes),
                            credentials=credentials,
                            allow=True,
                        )
                        return self.redirect(uri, application, token)

        except OAuthToolkitError as error:
            return self.error_response(error, application)

        if not application.custom_template:
            return self.render_to_response(self.get_context_data(**kwargs))
        else:
            credentials.pop('request')  # object can not json serialize
            request.session['credentials'] = credentials
            request.session['scopes'] = scopes

            template = Template(application.custom_template) 
            rendered_template = template.render(RequestContext(request))
            print(rendered_template)
            return HttpResponse(rendered_template)

            # return TemplateResponse(request, template, {})

            # response = HttpResponse(application.custom_template)
            # return response 

    def redirect(self, redirect_to, application, token=None):

        if not redirect_to.startswith("urn:ietf:wg:oauth:2.0:oob"):
            return super().redirect(redirect_to, application)

        parsed_redirect = urllib.parse.urlparse(redirect_to)
        code = urllib.parse.parse_qs(parsed_redirect.query)["code"][0]

        if redirect_to.startswith("urn:ietf:wg:oauth:2.0:oob:auto"):

            response = {
                "access_token": code,
                "token_uri": redirect_to,
                "client_id": application.client_id,
                "client_secret": application.client_secret,
                "revoke_uri": reverse("api:revoke-token"),
            }

            return JsonResponse(response)

        else:
            return render(
                request=self.request,
                template_name="oauth2_provider/authorized-oob.html",
                context={
                    "code": code,
                },
            )


@method_decorator(csrf_exempt, name="dispatch")
class TokenView(OAuthLibMixin, View):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """

    @method_decorator(sensitive_post_parameters("password"))
    def post(self, request, *args, **kwargs):
        tenant_uuid = kwargs.get('tenant_uuid')
        if tenant_uuid:
            tenant = Tenant.objects.get(uuid=tenant_uuid)
        else:
            tenant = None

        url, headers, body, status = self.create_token_response(request, tenant)
        if status == 200:
            access_token = json.loads(body).get("access_token")
            if access_token is not None:
                token = get_access_token_model().objects.get(token=access_token)
                app_authorized.send(sender=self, request=request, token=token)
        response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response


@method_decorator(csrf_exempt, name="dispatch")
class RevokeTokenView(OAuthLibMixin, View):
    """
    Implements an endpoint to revoke access or refresh tokens
    """

    def post(self, request, *args, **kwargs):
        url, headers, body, status = self.create_revocation_response(request)
        response = HttpResponse(content=body or "", status=status)

        for k, v in headers.items():
            response[k] = v
        return response
