"""
This module is largely inspired by django-rest-framework settings.

Settings for the OAuth2 Provider are all namespaced in the OAUTH2_PROVIDER setting.
For example your project's `settings.py` file might look like this:

OAUTH2_PROVIDER = {
    "CLIENT_ID_GENERATOR_CLASS":
        "oauth2_provider.generators.ClientIdGenerator",
    "CLIENT_SECRET_GENERATOR_CLASS":
        "oauth2_provider.generators.ClientSecretGenerator",
}

This module provides the `oauth2_settings` object, that is used to access
OAuth2 Provider settings, checking for user settings first, then falling
back to the defaults.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest
from django.test.signals import setting_changed
from django.urls import reverse
from django.utils.module_loading import import_string
from oauthlib.common import Request


USER_SETTINGS = getattr(settings, "OAUTH2_PROVIDER", None)

APPLICATION_MODEL = getattr(settings, "OAUTH2_PROVIDER_APPLICATION_MODEL", "oauth2_provider.Application")
ACCESS_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL", "oauth2_provider.AccessToken")
ID_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_ID_TOKEN_MODEL", "oauth2_provider.IDToken")
GRANT_MODEL = getattr(settings, "OAUTH2_PROVIDER_GRANT_MODEL", "oauth2_provider.Grant")
REFRESH_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL", "oauth2_provider.RefreshToken")

DEFAULTS = {
    "CLIENT_ID_GENERATOR_CLASS": "oauth2_provider.generators.ClientIdGenerator",
    "CLIENT_SECRET_GENERATOR_CLASS": "oauth2_provider.generators.ClientSecretGenerator",
    "CLIENT_SECRET_GENERATOR_LENGTH": 128,
    "ACCESS_TOKEN_GENERATOR": None,
    "REFRESH_TOKEN_GENERATOR": None,
    "EXTRA_SERVER_KWARGS": {},
    "OAUTH2_SERVER_CLASS": "oauthlib.oauth2.Server",
    "OIDC_SERVER_CLASS": "oauthlib.openid.Server",
    "OAUTH2_VALIDATOR_CLASS": "oauth2_provider.oauth2_validators.OAuth2Validator",
    "OAUTH2_BACKEND_CLASS": "oauth2_provider.oauth2_backends.OAuthLibCore",
    "SCOPES": {"read": "Reading scope", "write": "Writing scope"},
    "DEFAULT_SCOPES": ["__all__"],
    "SCOPES_BACKEND_CLASS": "oauth2_provider.scopes.SettingsScopes",
    "READ_SCOPE": "read",
    "WRITE_SCOPE": "write",
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 60,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 36000,
    "ID_TOKEN_EXPIRE_SECONDS": 36000,
    "REFRESH_TOKEN_EXPIRE_SECONDS": None,
    "REFRESH_TOKEN_GRACE_PERIOD_SECONDS": 0,
    "ROTATE_REFRESH_TOKEN": True,
    "ERROR_RESPONSE_WITH_SCOPES": False,
    "APPLICATION_MODEL": APPLICATION_MODEL,
    "ACCESS_TOKEN_MODEL": ACCESS_TOKEN_MODEL,
    "ID_TOKEN_MODEL": ID_TOKEN_MODEL,
    "GRANT_MODEL": GRANT_MODEL,
    "REFRESH_TOKEN_MODEL": REFRESH_TOKEN_MODEL,
    "APPLICATION_ADMIN_CLASS": "oauth2_provider.admin.ApplicationAdmin",
    "ACCESS_TOKEN_ADMIN_CLASS": "oauth2_provider.admin.AccessTokenAdmin",
    "GRANT_ADMIN_CLASS": "oauth2_provider.admin.GrantAdmin",
    "ID_TOKEN_ADMIN_CLASS": "oauth2_provider.admin.IDTokenAdmin",
    "REFRESH_TOKEN_ADMIN_CLASS": "oauth2_provider.admin.RefreshTokenAdmin",
    "REQUEST_APPROVAL_PROMPT": "auto",
    "ALLOWED_REDIRECT_URI_SCHEMES": ["http", "https"],
    "OIDC_ENABLED": False,
    "OIDC_ISS_ENDPOINT": "",
    "OIDC_USERINFO_ENDPOINT": "",
    "OIDC_RSA_PRIVATE_KEY": "",
    "OIDC_RESPONSE_TYPES_SUPPORTED": [
        "code",
        "token",
        "id_token",
        "id_token token",
        "code token",
        "code id_token",
        "code id_token token",
    ],
    "OIDC_SUBJECT_TYPES_SUPPORTED": ["public"],
    "OIDC_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED": [
        "client_secret_post",
        "client_secret_basic",
    ],
    # Special settings that will be evaluated at runtime
    "_SCOPES": [],
    "_DEFAULT_SCOPES": [],
    # Resource Server with Token Introspection
    "RESOURCE_SERVER_INTROSPECTION_URL": None,
    "RESOURCE_SERVER_AUTH_TOKEN": None,
    "RESOURCE_SERVER_INTROSPECTION_CREDENTIALS": None,
    "RESOURCE_SERVER_TOKEN_CACHING_SECONDS": 36000,
    # Whether or not PKCE is required
    "PKCE_REQUIRED": False,
    # Whether to re-create OAuthlibCore on every request.
    # Should only be required in testing.
    "ALWAYS_RELOAD_OAUTHLIB_CORE": False,
}

# List of settings that cannot be empty
MANDATORY = (
    "CLIENT_ID_GENERATOR_CLASS",
    "CLIENT_SECRET_GENERATOR_CLASS",
    "OAUTH2_SERVER_CLASS",
    "OAUTH2_VALIDATOR_CLASS",
    "OAUTH2_BACKEND_CLASS",
    "SCOPES",
    "ALLOWED_REDIRECT_URI_SCHEMES",
    "OIDC_RESPONSE_TYPES_SUPPORTED",
    "OIDC_SUBJECT_TYPES_SUPPORTED",
    "OIDC_TOKEN_ENDPOINT_AUTH_METHODS_SUPPORTED",
)

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    "CLIENT_ID_GENERATOR_CLASS",
    "CLIENT_SECRET_GENERATOR_CLASS",
    "ACCESS_TOKEN_GENERATOR",
    "REFRESH_TOKEN_GENERATOR",
    "OAUTH2_SERVER_CLASS",
    "OAUTH2_VALIDATOR_CLASS",
    "OAUTH2_BACKEND_CLASS",
    "SCOPES_BACKEND_CLASS",
    "APPLICATION_ADMIN_CLASS",
    "ACCESS_TOKEN_ADMIN_CLASS",
    "GRANT_ADMIN_CLASS",
    "ID_TOKEN_ADMIN_CLASS",
    "REFRESH_TOKEN_ADMIN_CLASS",
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class OAuth2ProviderSettings:
    """
    A settings object, that allows OAuth2 Provider settings to be accessed as properties.

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self._user_settings = user_settings or {}
        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self.mandatory = mandatory or ()
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "OAUTH2_PROVIDER", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid OAuth2Provider setting: %s" % attr)
        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            # Special case OAUTH2_SERVER_CLASS - if not specified, and OIDC is
            # enabled, use the OIDC_SERVER_CLASS setting instead
            if attr == "OAUTH2_SERVER_CLASS" and self.OIDC_ENABLED:
                val = self.defaults["OIDC_SERVER_CLASS"]
            else:
                val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        # Overriding special settings
        if attr == "_SCOPES":
            val = list(self.SCOPES.keys())
        if attr == "_DEFAULT_SCOPES":
            if "__all__" in self.DEFAULT_SCOPES:
                # If DEFAULT_SCOPES is set to ["__all__"] the whole set of scopes is returned
                val = list(self._SCOPES)
            else:
                # Otherwise we return a subset (that can be void) of SCOPES
                val = []
                for scope in self.DEFAULT_SCOPES:
                    if scope in self._SCOPES:
                        val.append(scope)
                    else:
                        raise ImproperlyConfigured("Defined DEFAULT_SCOPES not present in SCOPES")

        self.validate_setting(attr, val)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("OAuth2Provider setting: %s is mandatory" % attr)

    @property
    def server_kwargs(self):
        """
        This is used to communicate settings to oauth server.

        Takes relevant settings and format them accordingly.
        There's also EXTRA_SERVER_KWARGS that can override every value
        and is more flexible regarding keys and acceptable values
        but doesn't have import string magic or any additional
        processing, callables have to be assigned directly.
        For the likes of signed_token_generator it means something like

        {"token_generator": signed_token_generator(privkey, **kwargs)}
        """
        kwargs = {
            key: getattr(self, value)
            for key, value in [
                ("token_expires_in", "ACCESS_TOKEN_EXPIRE_SECONDS"),
                ("refresh_token_expires_in", "REFRESH_TOKEN_EXPIRE_SECONDS"),
                ("token_generator", "ACCESS_TOKEN_GENERATOR"),
                ("refresh_token_generator", "REFRESH_TOKEN_GENERATOR"),
            ]
        }
        kwargs.update(self.EXTRA_SERVER_KWARGS)
        return kwargs

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")
    
    def oidc_issuer(self, request):
        """
        Helper function to get the OIDC issuer URL, either from the settings
        or constructing it from the passed request.

        If only an oauthlib request is available, a dummy django request is
        built from that and used to generate the URL.
        """
        # code=NSi6ZGPOusmyqvwlXko70kbewDMcol&grant_type=authorization_code&tenant_uuid=3efed4d9-f2ee-455e-b868-6f60ea8fdff6
        body = request.body
        tenant = ''
        if body:
            arrs = body.split('&')
            for item in arrs:
                if 'tenant_uuid=' in item:
                    tenant = item[12:]
        if self.OIDC_ISS_ENDPOINT:
            return self.OIDC_ISS_ENDPOINT
        if isinstance(request, HttpRequest):
            django_request = request
        elif isinstance(request, Request):
            django_request = HttpRequest()
            django_request.META = request.headers
        else:
            raise TypeError("request must be a django or oauthlib request: got %r" % request)
        if tenant:
            abs_url = django_request.build_absolute_uri(reverse("api:oauth2_authorization_server:oidc-connect-discovery-info", args=[tenant]))
        else:
            abs_url = ''
        return abs_url[: -len("/.well-known/openid-configuration/")]

    def oidc_issuer(self, request, tenant):
        """
        Helper function to get the OIDC issuer URL, either from the settings
        or constructing it from the passed request.

        If only an oauthlib request is available, a dummy django request is
        built from that and used to generate the URL.
        """
        # code=NSi6ZGPOusmyqvwlXko70kbewDMcol&grant_type=authorization_code&tenant_uuid=3efed4d9-f2ee-455e-b868-6f60ea8fdff6
        body = request.body
        if body:
            arrs = body.split('&')
            tenant = ''
            for item in arrs:
                if 'tenant_uuid=' in item:
                    tenant = item[12:]
        if self.OIDC_ISS_ENDPOINT:
            return self.OIDC_ISS_ENDPOINT
        if isinstance(request, HttpRequest):
            django_request = request
        elif isinstance(request, Request):
            django_request = HttpRequest()
            django_request.META = request.headers
        else:
            raise TypeError("request must be a django or oauthlib request: got %r" % request)
        if tenant:
            abs_url = django_request.build_absolute_uri(reverse("api:oauth2_authorization_server:oidc-connect-discovery-info", args=[tenant]))
        else:
            abs_url = ''
        return abs_url[: -len("/.well-known/openid-configuration/")]


oauth2_settings = OAuth2ProviderSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)


def reload_oauth2_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "OAUTH2_PROVIDER":
        oauth2_settings.reload()


setting_changed.connect(reload_oauth2_settings)
