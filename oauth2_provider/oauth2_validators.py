import base64
import binascii
import logging
import re
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from urllib.parse import unquote_plus

import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, QuerySet
from django.urls import reverse
from django.utils import timezone, dateformat
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _
from .exceptions import FatalClientError
from .models import (
    AbstractApplication, get_access_token_model, get_oidc_application_model,
    get_application_model, get_grant_model, get_oidc_grant_model, get_refresh_token_model,
    get_oidc_access_token_model, get_oidc_refresh_token_model,
)
from .scopes import get_scopes_backend
from .settings import oauth2_settings
from oauthlib.oauth2 import RequestValidator

log = logging.getLogger("oauth2_provider")

GRANT_TYPE_MAPPING = {
    "authorization_code": (AbstractApplication.GRANT_AUTHORIZATION_CODE,),
    "password": (AbstractApplication.GRANT_PASSWORD,),
    "client_credentials": (AbstractApplication.GRANT_CLIENT_CREDENTIALS,),
    "refresh_token": (
        AbstractApplication.GRANT_AUTHORIZATION_CODE,
        AbstractApplication.GRANT_PASSWORD,
        AbstractApplication.GRANT_CLIENT_CREDENTIALS,
    ),
    "oidc_code_and_hybrid_flow": (get_oidc_application_model().CODE,
                                  get_oidc_application_model().CODE_TOKEN,
                                  get_oidc_application_model().CODE_IDTOKEN,
                                  get_oidc_application_model().CODE_IDTOKEN_TOKEN,
                                  ),
}

Application = get_application_model()
OidcApplication = get_oidc_application_model()
AccessToken = get_access_token_model()
OidcAccessToken = get_oidc_access_token_model()
Grant = get_grant_model()
OidcGrant = get_oidc_grant_model()
RefreshToken = get_refresh_token_model()
OidcRefreshToken = get_oidc_refresh_token_model()
UserModel = get_user_model()


class OAuth2Validator(RequestValidator):
    def _extract_basic_auth(self, request):
        """
        Return authentication string if request contains basic auth credentials,
        otherwise return None
        """
        auth = request.headers.get("HTTP_AUTHORIZATION", None)
        if not auth:
            return None

        splitted = auth.split(" ", 1)
        if len(splitted) != 2:
            return None
        auth_type, auth_string = splitted

        if auth_type != "Basic":
            return None

        return auth_string

    def _authenticate_basic_auth(self, request):
        """
        Authenticates with HTTP Basic Auth.

        Note: as stated in rfc:`2.3.1`, client_id and client_secret must be encoded with
        "application/x-www-form-urlencoded" encoding algorithm.
        """
        auth_string = self._extract_basic_auth(request)
        if not auth_string:
            return False

        try:
            encoding = request.encoding or settings.DEFAULT_CHARSET or "utf-8"
        except AttributeError:
            encoding = "utf-8"

        try:
            b64_decoded = base64.b64decode(auth_string)
        except (TypeError, binascii.Error):
            log.debug("Failed basic auth: %r can't be decoded as base64", auth_string)
            return False

        try:
            auth_string_decoded = b64_decoded.decode(encoding)
        except UnicodeDecodeError:
            log.debug(
                "Failed basic auth: %r can't be decoded as unicode by %r",
                auth_string, encoding
            )
            return False

        try:
            client_id, client_secret = map(unquote_plus, auth_string_decoded.split(":", 1))
        except ValueError:
            log.debug("Failed basic auth, Invalid base64 encoding.")
            return False

        if self._load_application(client_id, request) is None:
            log.debug("Failed basic auth: Application %s does not exist" % client_id)
            return False
        elif request.client.client_id != client_id:
            log.debug("Failed basic auth: wrong client id %s" % client_id)
            return False
        elif request.client.client_secret != client_secret:
            log.debug("Failed basic auth: wrong client secret %s" % client_secret)
            return False
        else:
            return True

    def _authenticate_request_body(self, request):
        """
        Try to authenticate the client using client_id and client_secret
        parameters included in body.

        Remember that this method is NOT RECOMMENDED and SHOULD be limited to
        clients unable to directly utilize the HTTP Basic authentication scheme.
        See rfc:`2.3.1` for more details.
        """
        # TODO: check if oauthlib has already unquoted client_id and client_secret
        try:
            client_id = request.client_id
            client_secret = request.client_secret
        except AttributeError:
            return False

        if self._load_application(client_id, request) is None:
            log.debug("Failed body auth: Application %s does not exists" % client_id)
            return False
        elif request.client.client_secret != client_secret:
            log.debug("Failed body auth: wrong client secret %s" % client_secret)
            return False
        else:
            return True

    def _load_application(self, client_id, request):
        """
        If request.client was not set, load application instance for given
        client_id and store it in request.client
        """

        # we want to be sure that request has the client attribute!
        assert hasattr(request, "client"), '"request" instance has no "client" attribute'
        try:
            if request.scopes and 'openid' in request.scopes:
                request.client = request.client or OidcApplication.objects.get(client_id=client_id)
            elif request.scopes and 'openid' not in request.scopes:
                request.client = request.client or Application.objects.get(client_id=client_id)
            elif not request.scopes:
                request.client = request.client or Application.objects.filter(
                    client_id=client_id) or OidcApplication.objects.filter(client_id=client_id)
            try:
                request.client = request.client[0] if isinstance(request.client, QuerySet) else request.client
            except IndexError:
                raise Application.DoesNotExist
            # Check that the application can be used (defaults to always True)
            if not request.client.is_usable(request):
                log.debug("Failed body authentication: Application %r is disabled" % (client_id))
                return None
            return request.client
        except (Application.DoesNotExist, OidcApplication.DoesNotExist):
            log.debug("Failed body authentication: Application %r does not exist" % (client_id))
            return None

    def _set_oauth2_error_on_request(self, request, access_token, scopes):
        if access_token is None:
            error = OrderedDict([
                ("error", "invalid_token",),
                ("error_description", _("The access token is invalid."),),
            ])
        elif access_token.is_expired():
            error = OrderedDict([
                ("error", "invalid_token",),
                ("error_description", _("The access token has expired."),),
            ])
        elif not access_token.allow_scopes(scopes):
            error = OrderedDict([
                ("error", "insufficient_scope",),
                ("error_description", _("The access token is valid but does not have enough scope."),),
            ])
        else:
            log.warning("OAuth2 access token is invalid for an unknown reason.")
            error = OrderedDict([
                ("error", "invalid_token",),
            ])
        request.oauth2_error = error
        return request

    def client_authentication_required(self, request, *args, **kwargs):
        """
        Determine if the client has to be authenticated

        This method is called only for grant types that supports client authentication:
            * Authorization code grant
            * Resource owner password grant
            * Refresh token grant

        If the request contains authorization headers, always authenticate the client
        no matter the grant type.

        If the request does not contain authorization headers, proceed with authentication
        only if the client is of type `Confidential`.

        If something goes wrong, call oauthlib implementation of the method.
        """
        if self._extract_basic_auth(request):
            return True

        try:
            if request.client_id and request.client_secret:
                return True
        except AttributeError:
            log.debug("Client ID or client secret not provided...")
            pass

        self._load_application(request.client_id, request)
        if request.client:
            return request.client.client_type == AbstractApplication.CLIENT_CONFIDENTIAL

        return super().client_authentication_required(request, *args, **kwargs)

    def authenticate_client(self, request, *args, **kwargs):
        """
        Check if client exists and is authenticating itself as in rfc:`3.2.1`

        First we try to authenticate with HTTP Basic Auth, and that is the PREFERRED
        authentication method.
        Whether this fails we support including the client credentials in the request-body,
        but this method is NOT RECOMMENDED and SHOULD be limited to clients unable to
        directly utilize the HTTP Basic authentication scheme.
        See rfc:`2.3.1` for more details
        """
        authenticated = self._authenticate_basic_auth(request)
        if not authenticated:
            authenticated = self._authenticate_request_body(request)
        return authenticated

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        """
        If we are here, the client did not authenticate itself as in rfc:`3.2.1` and we can
        proceed only if the client exists and is not of type "Confidential".
        """
        if self._load_application(client_id, request) is not None:
            log.debug("Application %r has type %r" % (client_id, request.client.client_type))
            return request.client.client_type != AbstractApplication.CLIENT_CONFIDENTIAL
        return False

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, *args, **kwargs):
        """
        Ensure the redirect_uri is listed in the Application instance redirect_uris field
        """
        grant = Grant.objects.get(code=code, application=client) if isinstance(client, Application) \
            else OidcGrant.objects.get(code=code, application=client)
        return grant.redirect_uri_allowed(redirect_uri)

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        """
        Remove the temporary grant used to swap the authorization token
        """
        grant = Grant.objects.get(code=code, application=request.client) if isinstance(request.client, Application) \
            else OidcGrant.objects.get(code=code, application=request.client)
        grant.delete()

    def validate_client_id(self, client_id, request, *args, **kwargs):
        """
        Ensure an Application exists with given client_id.
        If it exists, it's assigned to request.client.
        """
        return self._load_application(client_id, request) is not None

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        return request.client.default_redirect_uri

    def _get_token_from_authentication_server(
            self, token, introspection_url, introspection_token, introspection_credentials
    ):
        """Use external introspection endpoint to "crack open" the token.
        :param introspection_url: introspection endpoint URL
        :param introspection_token: Bearer token
        :param introspection_credentials: Basic Auth credentials (id,secret)
        :return: :class:`models.AccessToken`

        Some RFC 7662 implementations (including this one) use a Bearer token while others use Basic
        Auth. Depending on the external AS's implementation, provide either the introspection_token
        or the introspection_credentials.

        If the resulting access_token identifies a username (e.g. Authorization Code grant), add
        that user to the UserModel. Also cache the access_token up until its expiry time or a
        configured maximum time.

        """
        headers = None
        if introspection_token:
            headers = {"Authorization": "Bearer {}".format(introspection_token)}
        elif introspection_credentials:
            client_id = introspection_credentials[0].encode("utf-8")
            client_secret = introspection_credentials[1].encode("utf-8")
            basic_auth = base64.b64encode(client_id + b":" + client_secret)
            headers = {"Authorization": "Basic {}".format(basic_auth.decode("utf-8"))}

        try:
            response = requests.post(
                introspection_url,
                data={"token": token}, headers=headers
            )
        except requests.exceptions.RequestException:
            log.exception("Introspection: Failed POST to %r in token lookup", introspection_url)
            return None

        try:
            content = response.json()
        except ValueError:
            log.exception("Introspection: Failed to parse response as json")
            return None

        if "active" in content and content["active"] is True:
            if "username" in content:
                user, _created = UserModel.objects.get_or_create(
                    **{UserModel.USERNAME_FIELD: content["username"]}
                )
            else:
                user = None

            max_caching_time = datetime.now() + timedelta(
                seconds=oauth2_settings.RESOURCE_SERVER_TOKEN_CACHING_SECONDS
            )

            if "exp" in content:
                expires = datetime.utcfromtimestamp(content["exp"])
                if expires > max_caching_time:
                    expires = max_caching_time
            else:
                expires = max_caching_time

            scope = content.get("scope", "")
            expires = make_aware(expires)

            access_token, _created = AccessToken \
                .objects.select_related("application", "user") \
                .update_or_create(token=token,
                                  defaults={
                                      "user": user,
                                      "application": None,
                                      "scope": scope,
                                      "expires": expires,
                                  })

            return access_token

    def validate_bearer_token(self, token, scopes, request):
        """
        When users try to access resources, check that provided token is valid
        """
        if not token:
            return False

        introspection_url = oauth2_settings.RESOURCE_SERVER_INTROSPECTION_URL
        introspection_token = oauth2_settings.RESOURCE_SERVER_AUTH_TOKEN
        introspection_credentials = oauth2_settings.RESOURCE_SERVER_INTROSPECTION_CREDENTIALS

        if re.search('oidc', request.uri):
            try:
                access_token = OidcAccessToken.objects.select_related("application", "user").get(token=token)
            except OidcAccessToken.DoesNotExist:
                access_token = None
        else:
            try:
                access_token = AccessToken.objects.select_related("application", "user").get(token=token)
            except AccessToken.DoesNotExist:
                access_token = None
        # if there is no token or it's invalid then introspect the token if there's an external OAuth server
        if not access_token or not access_token.is_valid(scopes):
            if introspection_url and (introspection_token or introspection_credentials):
                access_token = self._get_token_from_authentication_server(
                    token,
                    introspection_url,
                    introspection_token,
                    introspection_credentials
                )
        if access_token and access_token.is_valid(scopes):
            request.client = access_token.application
            request.user = access_token.user
            request.scopes = scopes

            # this is needed by django rest framework
            request.access_token = access_token
            return True
        else:
            self._set_oauth2_error_on_request(request, access_token, scopes)
            return False

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        try:
            grant = Grant.objects.get(code=code, application=client) if isinstance(client, Application) \
                else OidcGrant.objects.get(code=code, application=client)

            # if isinstance(grant, OidcGrant) and grant.code_challenge_method:
            #     code_challenge = None
            #
            #     if grant.code_challenge_method == 'S256':
            #         code_challenge = base64.urlsafe_b64encode(
            #             hashlib.sha256(request.code_challenge.encode('ascii')).digest()
            #         ).decode('utf-8').replace('=', '')
            #
            #     if grant.code_challenge_method == 'plain':
            #         code_challenge = request.code_challenge
            #
            #     if not (code_challenge == grant.code_challenge):
            #         return False

            if not grant.is_expired():
                request.scopes = grant.scope.split(" ")
                request.user = grant.user
                return True
            return False

        except (Grant.DoesNotExist, OidcGrant.DoesNotExist):
            return False

    def get_code_challenge(self, code, request, *args, **kwargs):
        try:
            grant = Grant.objects.get(code=code, application=request.client) if isinstance(request.client, Application) \
                else OidcGrant.objects.get(code=code, application=request.client)
            return getattr(grant, "code_challenge", None)

        except (Grant.DoesNotExist, OidcGrant.DoesNotExist):
            return None

    def get_code_challenge_method(self, code, request):
        try:
            grant = Grant.objects.get(code=code, application=request.client) if isinstance(request.client, Application) \
                else OidcGrant.objects.get(code=code, application=request.client)
            return getattr(grant, "code_challenge_method", None)

        except (Grant.DoesNotExist, OidcGrant.DoesNotExist):
            return None

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        """
        Validate both grant_type is a valid string and grant_type is allowed for current workflow
        """
        assert (grant_type in GRANT_TYPE_MAPPING)  # mapping misconfiguration
        if isinstance(client, Application):
            return request.client.allows_grant_type(*GRANT_TYPE_MAPPING[grant_type])
        return request.client.allows_grant_type(*GRANT_TYPE_MAPPING['oidc_code_and_hybrid_flow'])

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        """
        We currently do not support the Authorization Endpoint Response Types registry as in
        rfc:`8.4`, so validate the response_type only if it matches "code" or "token"
        """
        if 'openid' not in request.scopes:
            if response_type == "code":
                return client.allows_grant_type(AbstractApplication.GRANT_AUTHORIZATION_CODE)
            elif response_type == "token":
                return client.allows_grant_type(AbstractApplication.GRANT_IMPLICIT)
            else:
                return False
        if response_type == "code":
            return client.allows_grant_type(get_oidc_application_model().CODE, get_oidc_application_model().CODE,
                                            get_oidc_application_model().CODE_TOKEN,
                                            get_oidc_application_model().CODE_IDTOKEN,
                                            get_oidc_application_model().CODE_IDTOKEN_TOKEN
                                            )
        elif response_type == "token":
            return client.allows_grant_type(get_oidc_application_model().IDTOKEN,
                                            get_oidc_application_model().IDTOKEN_TOKEN)
        else:
            return False

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        """
        Ensure required scopes are permitted (as specified in the settings file)
        """
        available_scopes = get_scopes_backend().get_available_scopes(application=client, request=request)
        return set(scopes).issubset(set(available_scopes))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        default_scopes = get_scopes_backend().get_default_scopes(application=request.client, request=request)
        return default_scopes

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        return request.client.redirect_uri_allowed(redirect_uri)

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        expires = timezone.now() + timedelta(
            seconds=oauth2_settings.AUTHORIZATION_CODE_EXPIRE_SECONDS)
        if 'openid' in request.scopes:
            g = OidcGrant(application=request.client, user=request.user, code=code["code"],
                          expires=expires, redirect_uri=request.redirect_uri,
                          scope=" ".join(request.scopes), nonce=request.nonce,
                          code_challenge=request.code_challenge)
            if request.code_challenge_method:
                g.code_challenge_method = request.code_challenge_method
        else:
            g = Grant(application=request.client, user=request.user, code=code["code"],
                      expires=expires, redirect_uri=request.redirect_uri,
                      scope=" ".join(request.scopes))
        g.save()

    def rotate_refresh_token(self, request):
        """
        Checks if rotate refresh token is enabled
        """
        return oauth2_settings.ROTATE_REFRESH_TOKEN

    @transaction.atomic
    def save_bearer_token(self, token, request, *args, **kwargs):
        """
        Save access and refresh token, If refresh token is issued, remove or
        reuse old refresh token as in rfc:`6`

        @see: https://tools.ietf.org/html/draft-ietf-oauth-v2-31#page-43
        """
        if "scope" not in token:
            raise FatalClientError("Failed to renew access token: missing scope")

        expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)

        if request.grant_type == "client_credentials":
            request.user = None

        # This comes from OAuthLib:
        # https://github.com/idan/oauthlib/blob/1.0.3/oauthlib/oauth2/rfc6749/tokens.py#L267
        # Its value is either a new random code; or if we are reusing
        # refresh tokens, then it is the same value that the request passed in
        # (stored in `request.refresh_token`)
        refresh_token_code = token.get("refresh_token", None)

        if refresh_token_code:
            # an instance of `RefreshToken` that matches the old refresh code.
            # Set on the request in `validate_refresh_token`
            refresh_token_instance = getattr(request, "refresh_token_instance", None)

            # If we are to reuse tokens, and we can: do so
            if not self.rotate_refresh_token(request) and \
                    isinstance(refresh_token_instance, RefreshToken) and \
                    refresh_token_instance.access_token:

                access_token = AccessToken.objects.select_for_update().get(
                    pk=refresh_token_instance.access_token.pk
                )
                access_token.user = request.user
                access_token.scope = token["scope"]
                access_token.expires = expires
                access_token.token = token["access_token"]
                access_token.application = request.client
                access_token.save()

            # else create fresh with access & refresh tokens
            else:
                # revoke existing tokens if possible to allow reuse of grant
                if isinstance(refresh_token_instance, RefreshToken):
                    # First, to ensure we don't have concurrency issues, we refresh the refresh token
                    # from the db while acquiring a lock on it
                    # We also put it in the "request cache"
                    refresh_token_instance = RefreshToken.objects.select_for_update().get(
                        id=refresh_token_instance.id
                    )
                    request.refresh_token_instance = refresh_token_instance

                    previous_access_token = AccessToken.objects.filter(
                        source_refresh_token=refresh_token_instance
                    ).first()
                    try:
                        refresh_token_instance.revoke()
                    except (AccessToken.DoesNotExist, RefreshToken.DoesNotExist):
                        pass
                    else:
                        setattr(request, "refresh_token_instance", None)
                else:
                    previous_access_token = None

                # If the refresh token has already been used to create an
                # access token (ie it's within the grace period), return that
                # access token
                if not previous_access_token:
                    access_token = self._create_access_token(
                        expires,
                        request,
                        token,
                        source_refresh_token=refresh_token_instance,
                    )
                    self._create_refresh_token(request, refresh_token_code, access_token)
                else:
                    # make sure that the token data we're returning matches
                    # the existing token
                    token["access_token"] = previous_access_token.token
                    token["refresh_token"] = previous_access_token.source_refresh_token.token
                    token["scope"] = previous_access_token.scope

        # No refresh token should be created, just access token
        else:
            self._create_access_token(expires, request, token)

        # TODO: check out a more reliable way to communicate expire time to oauthlib
        token["expires_in"] = oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS

    def _create_access_token(self, expires, request, token, source_refresh_token=None):
        if isinstance(request.client, Application):
            access_token = AccessToken(
                user=request.user,
                scope=token["scope"],
                expires=expires,
                token=token["access_token"],
                application=request.client,
                source_refresh_token=source_refresh_token,
            )
        else:
            access_token = OidcAccessToken(
                user=request.user,
                scope=token["scope"],
                expires=expires,
                token=token["access_token"],
                application=request.client,
                source_refresh_token=source_refresh_token,
            )
            code = OidcGrant.objects.get(code=request.code)
            id_token = self.create_id_token(access_token, request.user, request.client.client_id, nonce=code.nonce,
                                            at_hash=access_token.at_hash, request=request, scope=None)
            access_token.id_token = id_token
        access_token.save()
        return access_token

    def _create_refresh_token(self, request, token, access_token):
        if isinstance(access_token, AccessToken):
            refresh_token = RefreshToken(
                user=request.user,
                token=token,
                application=request.client,
                access_token=access_token
            )
        else:
            refresh_token = OidcRefreshToken(
                user=request.user,
                token=token,
                application=request.client,
                access_token=access_token
            )
        refresh_token.save()

    def revoke_token(self, token, token_type_hint, request, *args, **kwargs):
        """
        Revoke an access or refresh token.

        :param token: The token string.
        :param token_type_hint: access_token or refresh_token.
        :param request: The HTTP Request (oauthlib.common.Request)
        """
        if token_type_hint not in ["access_token", "refresh_token"]:
            token_type_hint = None

        token_types = {
            "access_token": AccessToken,
            "refresh_token": RefreshToken,
        }

        token_type = token_types.get(token_type_hint, AccessToken)
        try:
            token_type.objects.get(token=token).revoke()
        except ObjectDoesNotExist:
            for other_type in [_t for _t in token_types.values() if _t != token_type]:
                # slightly inefficient on Python2, but the queryset contains only one instance
                list(map(lambda t: t.revoke(), other_type.objects.filter(token=token)))

    def validate_user(self, username, password, client, request, *args, **kwargs):
        """
        Check username and password correspond to a valid and active User
        """
        u = authenticate(username=username, password=password)
        if u is not None and u.is_active:
            request.user = u
            return True
        return False

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Avoid second query for RefreshToken since this method is invoked *after*
        # validate_refresh_token.
        rt = request.refresh_token_instance
        if not rt.access_token_id:
            return AccessToken.objects.get(source_refresh_token_id=rt.id).scope

        return rt.access_token.scope

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        """
        Check refresh_token exists and refers to the right client.
        Also attach User instance to the request object
        """

        null_or_recent = Q(revoked__isnull=True) | Q(
            revoked__gt=timezone.now() - timedelta(
                seconds=oauth2_settings.REFRESH_TOKEN_GRACE_PERIOD_SECONDS
            )
        )
        rt = RefreshToken.objects.filter(null_or_recent, token=refresh_token).first()

        if not rt:
            return False

        request.user = rt.user
        request.refresh_token = rt.token
        # Temporary store RefreshToken instance to be reused by get_original_scopes and save_bearer_token.
        request.refresh_token_instance = rt
        return rt.application == client

    def create_id_token(self, token: str, user: UserModel, aud: str, nonce='', at_hash='', request=None, scope=None) -> dict:
        """
        Creates the id_token dictionary.
        See: http://openid.net/specs/openid-connect-core-1_0.html#IDToken
        Return a dic.
        """
        if scope is None:
            scope = []
        sub = str(user.uuid)
        expires_in = oauth2_settings.OIDC_ID_TOKEN_EXPIRE

        # Convert datetimes into timestamps.
        now = int(time.time())
        iat_time = now
        exp_time = int(now + expires_in)
        user_auth_time = user.last_active_time
        auth_time = int(dateformat.format(user_auth_time, 'U'))

        dic = {
            'iss': get_issuer(request=request),
            'sub': sub,
            'aud': str(aud),
            'exp': exp_time,
            'iat': iat_time,
            'auth_time': auth_time,
        }

        if nonce:
            dic['nonce'] = str(nonce)

        if at_hash:
            dic['at_hash'] = at_hash

        # Inlude (or not) user standard claims in the id_token.
        if oauth2_settings.OIDC_ID_TOKEN_INCLUDE_CLAIMS:
            # if settings.get('OIDC_EXTRA_SCOPE_CLAIMS'):
            #     custom_claims = settings.get('OIDC_EXTRA_SCOPE_CLAIMS', import_str=True)(token)
            #     claims = custom_claims.create_response_dic()
            # else:
            #     claims = StandardScopeClaims(token).create_response_dic()
            # dic.update(claims)
            pass

        dic = run_processing_hook(
            dic, id_token_processing_hook,
            user=user, token=token, request=request)
        return dic

    # def decode_id_token(self, token, client):
    #     """
    #     Represent the ID Token as a JSON Web Token (JWT).
    #     Return a hash.
    #     """
    #     keys = get_client_alg_keys(client)
    #     return JWS().verify_compact(token, keys=keys)
    #
    # def client_id_from_id_token(self, id_token):
    #     """
    #     Extracts the client id from a JSON Web Token (JWT).
    #     Returns a string or None.
    #     """
    #     payload = JWT().unpack(id_token).payload()
    #     aud = payload.get('aud', None)
    #     if aud is None:
    #         return None
    #     if isinstance(aud, list):
    #         return aud[0]
    #     return aud

    def refactor_oidc_authorization_uri(self, response_type, access_token, id_token, uri) -> str:
        """
        Refactoring the authorization uris for various oidc applications.
            1)code token;
            for example: https://www.longguikeji.com/#access_token=eyJhbGciOiJSUzI1&code=eyJhbGciOiJSUzI1N

            2)code id_token;
            for example: https://www.longguikeji.com/#id_token=eyJhbGciOiJSUzI1&code=eyJhbGciOiJSUzI1N

            3)code id_token token;
            for example: https://www.longguikeji.com/#access_token=eyJhbGciOiJSUzI1&code=eyJhbGciOiJSUzI1N&id_token=eyJhbGciOiJSUzI1

            4)id_token token;
            for example: https://www.longguikeji.com/#access_token=eyJhbGciOiJSUzI1&id_token=eyJhbGciOiJSUzI1

            5)id_token;
            for example: https://www.longguikeji.com/#id_token=eyJhbGciOiJSUzI1
        """
        if response_type == 'code token':
            uri += '&access_token={0}'.format(access_token.token)

        elif response_type == 'code id_token':
            uri += '&id_token={0}'.format(id_token)

        elif response_type == 'code id_token token':
            uri += '&access_token={0}&id_token={1}'.format(access_token.token, id_token)

        elif response_type == 'id_token token':
            uri += '&id_token={0}'.format(id_token)

        elif response_type == 'id_token':
            uri = re.sub(re.search(r"access_token=.*?&", uri).group(), '', uri) + '&id_token={0}'.format(id_token)

        return uri


def get_site_url(site_url=None, request=None) -> str:
    """
    Construct the site url.
    Orders to decide site url:
        1. valid `site_url` parameter
        2. valid `OIDC_SITE_URL` in settings
        3. construct from `request` object
    """
    site_url = site_url or oauth2_settings.OIDC_SITE_URL
    if site_url:
        return site_url
    elif request:
        return '{}://{}'.format(request.scheme, request.get_host())
    else:
        raise Exception('Either pass `site_url`, '
                        'or set `SITE_URL` in settings, '
                        'or pass `request` object.')


def get_issuer(site_url=None, request=None) -> str:
    """
    Construct the issuer full url. Basically is the site url with some path
    appended.
    """
    site_url = get_site_url(site_url=site_url, request=request)
    path = reverse('oauth2_provider:provider-info').split('/.well-known/openid-configuration')[0]
    issuer = site_url + path
    return str(issuer)


def run_processing_hook(subject, *processing_hooks, **kwargs):
    # processing_hooks = settings.get(hook_settings_name)
    if not isinstance(processing_hooks, (list, tuple)):
        processing_hooks = [processing_hooks]

    for processing_hook in processing_hooks:
        subject = processing_hook(subject, **kwargs)

    return subject


def id_token_processing_hook(
        id_token, user, token, request, **kwargs):
    """
    Hook to perform some additional actions to `id_token` dictionary just before serialization.

    :param id_token: dictionary contains values that going to be serialized into `id_token`
    :type id_token: dict

    :param user: user for whom id_token is generated
    :type user: User

    :param token: the Token object created for the authentication request
    :type token: oidc_provider.models.Token

    :param request: the request initiating this ID token processing
    :type request: django.http.HttpRequest

    :return: custom modified dictionary of values for `id_token`
    :rtype: dict
    """
    return id_token
