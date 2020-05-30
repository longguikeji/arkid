import json
from urllib.parse import urlparse, urlunparse, parse_qs
from oauthlib import oauth2
from oauthlib.common import quote, urlencode, urlencoded
from .exceptions import FatalClientError, OAuthToolkitError
from .settings import oauth2_settings


class OAuthLibCore(object):
    """
    TODO: add docs
    """
    def __init__(self, server=None):
        """
        :params server: An instance of oauthlib.oauth2.Server class
        """
        self.server = server or oauth2_settings.OAUTH2_SERVER_CLASS(oauth2_settings.OAUTH2_VALIDATOR_CLASS())

    def _get_escaped_full_path(self, request):
        """
        Django considers "safe" some characters that aren't so for oauthlib.
        We have to search for them and properly escape.
        """
        parsed = list(urlparse(request.get_full_path()))
        unsafe = set(c for c in parsed[4]).difference(urlencoded)
        for c in unsafe:
            parsed[4] = parsed[4].replace(c, quote(c, safe=b""))

        return urlunparse(parsed)

    def _get_extra_credentials(self, request):
        """
        Produce extra credentials for token response. This dictionary will be
        merged with the response.
        See also: `oauthlib.oauth2.rfc6749.TokenEndpoint.create_token_response`

        :param request: The current django.http.HttpRequest object
        :return: dictionary of extra credentials or None (default)
        """
        return None

    def _extract_params(self, request):
        """
        Extract parameters from the Django request object.
        Such parameters will then be passed to OAuthLib to build its own
        Request object. The body should be encoded using OAuthLib urlencoded.
        """
        uri = self._get_escaped_full_path(request)
        http_method = request.method
        headers = self.extract_headers(request)
        body = urlencode(self.extract_body(request))
        return uri, http_method, body, headers

    def extract_headers(self, request):
        """
        Extracts headers from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: a dictionary with OAuthLib needed headers
        """
        headers = request.META.copy()
        if "wsgi.input" in headers:
            del headers["wsgi.input"]
        if "wsgi.errors" in headers:
            del headers["wsgi.errors"]
        if "HTTP_AUTHORIZATION" in headers:
            headers["Authorization"] = headers["HTTP_AUTHORIZATION"]

        return headers

    def extract_body(self, request):
        """
        Extracts the POST body from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: provided POST parameters
        """
        return request.POST.items()

    def validate_authorization_request(self, request):
        """
        A wrapper method that calls validate_authorization_request on `server_class` instance.

        :param request: The current django.http.HttpRequest object
        """
        try:
            uri, http_method, body, headers = self._extract_params(request)
            uri, nonce, code_challenge, code_challenge_method = self.additional_authorization_for_oidc('uri', uri=uri)
            scopes, credentials = self.server.validate_authorization_request(
                uri, http_method=http_method, body=body, headers=headers)  # oauthlib.oauth2.rfc6749.endpoints.pre_configured.Server -> oauthlib.oauth2.rfc6749.endpoints.authorization.AuthorizationEndpoint -> oauthlib.oauth2.rfc6749.grant_types.authorization_code.AuthorizationCodeGrant
            credentials = self.additional_authorization_for_oidc('credentials', scopes=scopes, credentials=credentials,
                                                                 nonce=nonce, code_challenge=code_challenge,
                                                                 code_challenge_method=code_challenge_method)
            return scopes, credentials
        except oauth2.FatalClientError as error:
            raise FatalClientError(error=error)
        except oauth2.OAuth2Error as error:
            raise OAuthToolkitError(error=error)

    def additional_authorization_for_oidc(self, option, **kwargs):
        if option == 'uri':
            path = urlparse(kwargs['uri']).path
            queryset = parse_qs(urlparse(kwargs['uri']).query, keep_blank_values=True, strict_parsing=True)

            if 'openid' not in queryset.get('scope', []):
                return kwargs['uri'], queryset.get('nonce', [''])[0],\
                   queryset.get('code_challenge', [''])[0], queryset.get('code_challenge_method', [''])[0]

            queryset['response_type'] = oauth2_settings.UP_COMPATIBLE_OIDC_RESPONSE_TYPE.get(
                queryset['response_type'][0], None).split()

            uri = ''
            for key, value in queryset.items():
                uri += key + '=' + value[0] + '&'
            uri = quote(uri[:-1], safe='=&')
            return "{0}?{1}".format(path, uri), queryset.get('nonce', [''])[0],\
                   queryset.get('code_challenge', [''])[0], queryset.get('code_challenge_method', [''])[0]

        if option == 'credentials' and 'openid' in kwargs['scopes']:
            kwargs['credentials'].update(nonce=kwargs['nonce'])
            kwargs['credentials'].update(code_challenge=kwargs['code_challenge'])
            kwargs['credentials'].update(code_challenge_method=kwargs['code_challenge_method'])
        return kwargs['credentials']

    def create_authorization_response(self, request, scopes, credentials, allow):
        """
        A wrapper method that calls create_authorization_response on `server_class`
        instance.

        :param request: The current django.http.HttpRequest object
        :param scopes: A list of provided scopes
        :param credentials: Authorization credentials dictionary containing
                           `client_id`, `state`, `redirect_uri`, `response_type`
        :param allow: True if the user authorize the client, otherwise False
        """
        try:
            if not allow:
                raise oauth2.AccessDeniedError(
                    state=credentials.get("state", None))

            # add current user to credentials. this will be used by OAUTH2_VALIDATOR_CLASS
            credentials["user"] = request.user

            headers, body, status = self.server.create_authorization_response(
                uri=credentials["redirect_uri"], scopes=scopes, credentials=credentials)
            uri = headers.get("Location", None)

            return uri, headers, body, status

        except oauth2.FatalClientError as error:
            raise FatalClientError(error=error, redirect_uri=credentials["redirect_uri"])
        except oauth2.OAuth2Error as error:
            raise OAuthToolkitError(error=error, redirect_uri=credentials["redirect_uri"])

    def create_token_response(self, request):
        """
        A wrapper method that calls create_token_response on `server_class` instance.

        :param request: The current django.http.HttpRequest object
        """
        uri, http_method, body, headers = self._extract_params(request)
        extra_credentials = self._get_extra_credentials(request)
        headers, body, status = self.server.create_token_response(uri, http_method, body,
                                                                  headers, extra_credentials)
        uri = headers.get("Location", None)
        return uri, headers, body, status

    def create_revocation_response(self, request):
        """
        A wrapper method that calls create_revocation_response on a
        `server_class` instance.

        :param request: The current django.http.HttpRequest object
        """
        uri, http_method, body, headers = self._extract_params(request)
        headers, body, status = self.server.create_revocation_response(
            uri, http_method, body, headers)
        uri = headers.get("Location", None)
        return uri, headers, body, status

    def verify_request(self, request, scopes):
        """
        A wrapper method that calls verify_request on `server_class` instance.

        :param request: The current django.http.HttpRequest object
        :param scopes: A list of scopes required to verify so that request is verified
        """
        uri, http_method, body, headers = self._extract_params(request)
        valid, r = self.server.verify_request(uri, http_method, body, headers, scopes=scopes)
        return valid, r


class JSONOAuthLibCore(OAuthLibCore):
    """
    Extends the default OAuthLibCore to parse correctly application/json requests
    """
    def extract_body(self, request):
        """
        Extracts the JSON body from the Django request object
        :param request: The current django.http.HttpRequest object
        :return: provided POST parameters "urlencodable"
        """
        try:
            body = json.loads(request.body.decode("utf-8")).items()
        except AttributeError:
            body = ""
        except ValueError:
            body = ""

        return body


class OidcLibCore(OAuthLibCore):

    def create_token_response(self, request):
        """
        A wrapper method that calls create_token_response on `server_class` instance.

        :param request: The current django.http.HttpRequest object
        """
        uri, http_method, body, headers = self._extract_params(request)
        extra_credentials = self._get_extra_credentials(request)
        headers, body, status = self.server.create_token_response(uri, http_method, body,
                                                                  headers, extra_credentials, HybridFlowGrant)
        uri = headers.get("Location", None)
        return uri, headers, body, status


from oauthlib.oauth2.rfc6749.grant_types.authorization_code import AuthorizationCodeGrant


class HybridFlowGrant(AuthorizationCodeGrant):
    # def validate_token_request(self, request):
    #     """
    #     :param request: OAuthlib request.
    #     :type request: oauthlib.common.Request
    #     """
    #     # REQUIRED. Value MUST be set to "authorization_code".
    #     if request.grant_type not in ('authorization_code', 'openid'):
    #         raise errors.UnsupportedGrantTypeError(request=request)
    #
    #     for validator in self.custom_validators.pre_token:
    #         validator(request)
    #
    #     if request.code is None:
    #         raise errors.InvalidRequestError(
    #             description='Missing code parameter.', request=request)
    #
    #     for param in ('client_id', 'grant_type', 'redirect_uri'):
    #         if param in request.duplicate_params:
    #             raise errors.InvalidRequestError(description='Duplicate %s parameter.' % param,
    #                                              request=request)
    #     if self.request_validator.client_authentication_required(request):
    #         # If the client type is confidential or the client was issued client
    #         # credentials (or assigned other authentication requirements), the
    #         # client MUST authenticate with the authorization server as described
    #         # in Section 3.2.1.
    #         # https://tools.ietf.org/html/rfc6749#section-3.2.1
    #         if not self.request_validator.authenticate_client(request):
    #             log.debug('Client authentication failed, %r.', request)
    #             raise errors.InvalidClientError(request=request)
    #     elif not self.request_validator.authenticate_client_id(request.client_id, request):
    #         # REQUIRED, if the client is not authenticating with the
    #         # authorization server as described in Section 3.2.1.
    #         # https://tools.ietf.org/html/rfc6749#section-3.2.1
    #         log.debug('Client authentication failed, %r.', request)
    #         raise errors.InvalidClientError(request=request)
    #     if not hasattr(request.client, 'client_id'):
    #         raise NotImplementedError('Authenticate client must set the '
    #                                   'request.client.client_id attribute '
    #                                   'in authenticate_client.')
    #     request.client_id = request.client_id or request.client.client_id
    #     # Ensure client is authorized use of this grant type
    #     self.validate_grant_type(request)
    #     # REQUIRED. The authorization code received from the
    #     # authorization server.
    #     if not self.request_validator.validate_code(request.client_id,
    #                                                 request.code, request.client, request):
    #         log.debug('Client, %r (%r), is not allowed access to scopes %r.',
    #                   request.client_id, request.client, request.scopes)
    #         raise errors.InvalidGrantError(request=request)
    #
    #     # OPTIONAL. Validate PKCE code_verifier
    #     challenge = self.request_validator.get_code_challenge(request.code, request)
    #
    #     if challenge is not None:
    #         if request.code_verifier is None:
    #             raise errors.MissingCodeVerifierError(request=request)
    #
    #         challenge_method = self.request_validator.get_code_challenge_method(request.code, request)
    #         if challenge_method is None:
    #             raise errors.InvalidGrantError(request=request, description="Challenge method not found")
    #
    #         if challenge_method not in self._code_challenge_methods:
    #             raise errors.ServerError(
    #                 description="code_challenge_method {} is not supported.".format(challenge_method),
    #                 request=request
    #             )
    #
    #         if not self.validate_code_challenge(challenge,
    #                                             challenge_method,
    #                                             request.code_verifier):
    #             log.debug('request provided a invalid code_verifier.')
    #             raise errors.InvalidGrantError(request=request)
    #     elif self.request_validator.is_pkce_required(request.client_id, request) is True:
    #         if request.code_verifier is None:
    #             raise errors.MissingCodeVerifierError(request=request)
    #         raise errors.InvalidGrantError(request=request, description="Challenge not found")
    #
    #     for attr in ('user', 'scopes'):
    #         if getattr(request, attr, None) is None:
    #             log.debug('request.%s was not set on code validation.', attr)
    #
    #     # REQUIRED, if the "redirect_uri" parameter was included in the
    #     # authorization request as described in Section 4.1.1, and their
    #     # values MUST be identical.
    #     if request.redirect_uri is None:
    #         request.using_default_redirect_uri = True
    #         request.redirect_uri = self.request_validator.get_default_redirect_uri(
    #             request.client_id, request)
    #         log.debug('Using default redirect_uri %s.', request.redirect_uri)
    #         if not request.redirect_uri:
    #             raise errors.MissingRedirectURIError(request=request)
    #     else:
    #         request.using_default_redirect_uri = False
    #         log.debug('Using provided redirect_uri %s', request.redirect_uri)
    #
    #     if not self.request_validator.confirm_redirect_uri(request.client_id, request.code,
    #                                                        request.redirect_uri, request.client,
    #                                                        request):
    #         log.debug('Redirect_uri (%r) invalid for client %r (%r).',
    #                   request.redirect_uri, request.client_id, request.client)
    #         raise errors.MismatchingRedirectURIError(request=request)
    #
    #     for validator in self.custom_validators.post_token:
    #         validator(request)

    def create_token_response(self, request, token_handler):
        """Validate the authorization code.

        The client MUST NOT use the authorization code more than once. If an
        authorization code is used more than once, the authorization server
        MUST deny the request and SHOULD revoke (when possible) all tokens
        previously issued based on that authorization code. The authorization
        code is bound to the client identifier and redirection URI.

        :param request: OAuthlib request.
        :type request: oauthlib.common.Request
        :param token_handler: A token handler instance, for example of type
                              oauthlib.oauth2.BearerToken.

        """
        headers = self._get_default_headers()
        # try:
            # self.validate_token_request(request)
        #     log.debug('Token request validation ok for %r.', request)
        # except errors.OAuth2Error as e:
        #     log.debug('Client error during validation of %r. %r.', request, e)
        #     headers.update(e.headers)
        #     return headers, e.json, e.status_code
        token = token_handler.create_token(request, refresh_token=self.refresh_token)
        for modifier in self._token_modifiers:
            token = modifier(token, token_handler, request)
        self.request_validator.save_token(token, request)
        # self.request_validator.invalidate_authorization_code(
        #     request.client_id, request.code, request)
        return headers, json.dumps(token), 200


def get_oauthlib_core():
    """
    Utility function that take a request and returns an instance of
    `oauth2_provider.backends.OAuthLibCore`
    """
    validator = oauth2_settings.OAUTH2_VALIDATOR_CLASS()
    server = oauth2_settings.OAUTH2_SERVER_CLASS(validator)
    return oauth2_settings.OAUTH2_BACKEND_CLASS(server)
