import json
import re
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from jwcrypto import jwk

from ..models import get_application_model
from ..settings import oauth2_settings
from .mixins import OAuthLibMixin, OIDCOnlyMixin
from oauth2_provider.models import AccessToken, IDToken
from arkid.core.models import Tenant, ExpiringToken


Application = get_application_model()


# class ConnectDiscoveryInfoView(OIDCOnlyMixin, View):
#     """
#     View used to show oidc provider configuration information
#     """

#     def get(self, request, *args, **kwargs):
#         from config import get_app_config

#         tenant = None
#         tenant_uuid = kwargs.get('tenant_uuid')
#         if tenant_uuid:
#             tenant = Tenant.objects.get(uuid=tenant_uuid)

#         if not tenant:
#             uuid_re = r"[0-9a-f]{8}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{4}\-[0-9a-f]{12}"
#             path = self.request.path
#             res = re.search(uuid_re, path)
#             if res:
#                 tenant_uuid = res.group(0)
#                 tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

#         issuer_url = oauth2_settings.OIDC_ISS_ENDPOINT
#         host = get_app_config().get_host()
#         if not issuer_url:
#             if tenant:
#                 issuer_url = oauth2_settings.oidc_issuer(request, tenant.uuid)
#                 authorization_endpoint = host+reverse("api:oauth2_authorization_server:authorize", args=[tenant.uuid])
#                 token_endpoint = host+reverse("api:oauth2_authorization_server:token", args=[tenant.uuid])
#                 userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[tenant.uuid])
#                 jwks_uri = host+reverse("api:oauth2_authorization_server:jwks-info", args=[tenant.uuid])
#             else:
#                 issuer_url = oauth2_settings.oidc_issuer(request)
#                 authorization_endpoint = host+reverse("api:arkid_saas:authorize-platform")
#                 token_endpoint = host+reverse("api:arkid_saas:token-platform")
#                 userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or host+reverse("api:arkid_saas:oauth-user-info-platform")
#                 jwks_uri = host+reverse("api:arkid_saas:jwks-info-platform")
#         else:
#             if tenant:
#                 authorization_endpoint = "{}{}".format(issuer_url, reverse("api:oauth2_authorization_server:authorize"))
#                 token_endpoint = "{}{}".format(issuer_url, reverse("api:oauth2_authorization_server:token"))
#                 userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or "{}{}".format(
#                     issuer_url, reverse("api:oauth2_authorization_server:user-info")
#                 )
#                 jwks_uri = "{}{}".format(issuer_url, reverse("api:oauth2_authorization_server:jwks-info"))
#             else:
#                 authorization_endpoint = "{}{}".format(issuer_url, reverse("api:arkid_saas:authorize"))
#                 token_endpoint = "{}{}".format(issuer_url, reverse("api:arkid_saas:token"))
#                 userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or "{}{}".format(
#                     issuer_url, reverse("api:arkid_saas:user-info")
#                 )
#                 jwks_uri = "{}{}".format(issuer_url, reverse("api:arkid_saas:jwks-info"))
#         signing_algorithms = [Application.HS256_ALGORITHM]
#         if oauth2_settings.OIDC_RSA_PRIVATE_KEY:
#             signing_algorithms = [Application.RS256_ALGORITHM, Application.HS256_ALGORITHM]
#         data = {
#             "issuer": issuer_url,
#             "authorization_endpoint": authorization_endpoint,
#             "token_endpoint": token_endpoint,
#             "userinfo_endpoint": userinfo_endpoint,
#             "jwks_uri": jwks_uri,
#             "response_types_supported": oauth2_settings.OIDC_RESPONSE_TYPES_SUPPORTED,
#             "subject_types_supported": oauth2_settings.OIDC_SUBJECT_TYPES_SUPPORTED,
#             "id_token_signing_alg_values_supported": signing_algorithms,
#             "token_endpoint_auth_methods_supported": (
#                 oauth2_settings.OIDC_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED
#             ),
#         }
#         response = JsonResponse(data)
#         response["Access-Control-Allow-Origin"] = "*"
#         return response


class ConnectDiscoveryInfoView(OIDCOnlyMixin, View):
    """
    View used to show oidc provider configuration information per
    `OpenID Provider Metadata <https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata>`_
    """

    def get(self, request, *args, **kwargs):
        issuer_url = oauth2_settings.OIDC_ISS_ENDPOINT

        if not issuer_url:
            issuer_url = oauth2_settings.oidc_issuer(request)
            authorization_endpoint = request.build_absolute_uri(reverse("oauth2_provider:authorize"))
            token_endpoint = request.build_absolute_uri(reverse("oauth2_provider:token"))
            userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or request.build_absolute_uri(
                reverse("oauth2_provider:user-info")
            )
            jwks_uri = request.build_absolute_uri(reverse("oauth2_provider:jwks-info"))
        else:
            parsed_url = urlparse(oauth2_settings.OIDC_ISS_ENDPOINT)
            host = parsed_url.scheme + "://" + parsed_url.netloc
            authorization_endpoint = "{}{}".format(host, reverse("oauth2_provider:authorize"))
            token_endpoint = "{}{}".format(host, reverse("oauth2_provider:token"))
            userinfo_endpoint = oauth2_settings.OIDC_USERINFO_ENDPOINT or "{}{}".format(
                host, reverse("oauth2_provider:user-info")
            )
            jwks_uri = "{}{}".format(host, reverse("oauth2_provider:jwks-info"))

        signing_algorithms = [Application.HS256_ALGORITHM]
        if oauth2_settings.OIDC_RSA_PRIVATE_KEY:
            signing_algorithms = [Application.RS256_ALGORITHM, Application.HS256_ALGORITHM]

        validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
        validator = validator_class()
        oidc_claims = list(set(validator.get_discovery_claims(request)))
        scopes_class = oauth2_settings.SCOPES_BACKEND_CLASS
        scopes = scopes_class()
        scopes_supported = [scope for scope in scopes.get_available_scopes()]

        data = {
            "issuer": issuer_url,
            "authorization_endpoint": authorization_endpoint,
            "token_endpoint": token_endpoint,
            "userinfo_endpoint": userinfo_endpoint,
            "jwks_uri": jwks_uri,
            "scopes_supported": scopes_supported,
            "response_types_supported": oauth2_settings.OIDC_RESPONSE_TYPES_SUPPORTED,
            "subject_types_supported": oauth2_settings.OIDC_SUBJECT_TYPES_SUPPORTED,
            "id_token_signing_alg_values_supported": signing_algorithms,
            "token_endpoint_auth_methods_supported": (
                oauth2_settings.OIDC_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED
            ),
            "claims_supported": oidc_claims,
        }
        response = JsonResponse(data)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class JwksInfoView(OIDCOnlyMixin, View):
    """
    View used to show oidc json web key set document
    """

    def get(self, request, *args, **kwargs):
        keys = []
        if oauth2_settings.OIDC_RSA_PRIVATE_KEY:
            key = jwk.JWK.from_pem(oauth2_settings.OIDC_RSA_PRIVATE_KEY.encode("utf8"))
            data = {"alg": "RS256", "use": "sig", "kid": key.thumbprint()}
            data.update(json.loads(key.export_public()))
            keys.append(data)
        response = JsonResponse({"keys": keys})
        response["Access-Control-Allow-Origin"] = "*"
        return response


@method_decorator(csrf_exempt, name="dispatch")
class UserInfoView(OIDCOnlyMixin, OAuthLibMixin, View):
    """
    View used to show Claims about the authenticated End-User
    """

    def get(self, request, *args, **kwargs):
        return self._create_userinfo_response(request)

    def post(self, request, *args, **kwargs):
        return self._create_userinfo_response(request)

    def _create_userinfo_response(self, request):
        url, headers, body, status = self.create_userinfo_response(request)
        response = HttpResponse(content=body or "", status=status)
        for k, v in headers.items():
            response[k] = v
        return response


@method_decorator(csrf_exempt, name="dispatch")
class UserInfoExtendView(UserInfoView):
    """
    View used to show Claims about the authenticated End-User
    """

    def get(self, request, *args, **kwargs):
        access_token = request.META.get('HTTP_AUTHORIZATION', '')
        return self.get_user(request, access_token)

    def post(self, request, *args, **kwargs):
        access_token = request.META.get('HTTP_AUTHORIZATION', '')
        return self.get_user(request, access_token)

    def get_user(self, request, access_token):
        if access_token:
            access_token = access_token.split(' ')[1]
            access_token = AccessToken.objects.filter(token=access_token).first()
            if access_token:
                user = access_token.user
                data = {"id":user.id,"name":user.username,"email":user.email}
                try:
                    response = self._create_userinfo_response(request)
                    resp_data = json.loads(response.content)
                    data.update(resp_data)
                    return JsonResponse(data)
                except Exception as e:
                     return JsonResponse({"error": str(e)})
            else:
                return JsonResponse({"error": "access_token 不存在"})
        else:
            return JsonResponse({"error": "access_token 不能为空"})


@method_decorator(csrf_exempt, name="dispatch")
class OIDCLogoutView(OIDCOnlyMixin, OAuthLibMixin, View):
    """
    View used to show Claims about the authenticated End-User
    """

    def get(self, request, *args, **kwargs):
        id_token_hint = request.GET.get('id_token_hint', '')
        url = request.GET.get('post_logout_redirect_uri', '')
        id_token = IDToken.objects.filter(token=id_token_hint).first()
        if id_token:
            user = id_token.user
            ExpiringToken.objects.filter(
                user=user
            ).delete()
            if url:
                return HttpResponseRedirect(url)
            else:
                return JsonResponse({"error_code":0, 'error_msg':'logout success'})
        else:
            return JsonResponse({"error_code":1, "error_msg": "id_token error"})