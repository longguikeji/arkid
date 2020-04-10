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
import importlib
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

USER_SETTINGS = getattr(settings, "OAUTH2_PROVIDER", None)

APPLICATION_MODEL = getattr(settings, "OAUTH2_PROVIDER_APPLICATION_MODEL", "oauth2_provider.Application")
OIDC_APPLICATION_MODEL = getattr(settings, "OAUTH2_PROVIDER_OIDC_APPLICATION_MODEL", "oauth2_provider.OidcApplication")
OIDC_ACCESS_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_OIDC_ACCESS_TOKEN_MODEL", "oauth2_provider.OidcAccessToken")
ACCESS_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL", "oauth2_provider.AccessToken")
OIDC_GRANT_MODEL = getattr(settings, "OAUTH2_PROVIDER_OIDC_GRANT_MODEL", "oauth2_provider.OidcGrant")
GRANT_MODEL = getattr(settings, "OAUTH2_PROVIDER_GRANT_MODEL", "oauth2_provider.Grant")
OIDC_REFRESH_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_OIDC_REFRESH_TOKEN_MODEL", "oauth2_provider.OidcRefreshToken")
REFRESH_TOKEN_MODEL = getattr(settings, "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL", "oauth2_provider.RefreshToken")
OIDC_RSA_KEY_MODEL = getattr(settings, "OAUTH2_PROVIDER_OIDC_RSA_KEY", "oauth2_provider.OidcRsaKey")

DEFAULTS = {
    "CLIENT_ID_GENERATOR_CLASS": "oauth2_provider.generators.ClientIdGenerator",
    "CLIENT_SECRET_GENERATOR_CLASS": "oauth2_provider.generators.ClientSecretGenerator",
    "CLIENT_SECRET_GENERATOR_LENGTH": 128,
    "OAUTH2_SERVER_CLASS": "oauthlib.oauth2.Server",
    "OAUTH2_VALIDATOR_CLASS": "oauth2_provider.oauth2_validators.OAuth2Validator",
    "OAUTH2_BACKEND_CLASS": "oauth2_provider.oauth2_backends.OAuthLibCore",
    "OIDC_BACKEND_CLASS": "oauth2_provider.oauth2_backends.OidcLibCore",
    "SCOPES": {"read": "Reading scope", "write": "Writing scope", "openid": "ID token scope", "introspect": "Token introspection"},
    "DEFAULT_SCOPES": ["__all__"],
    "SCOPES_BACKEND_CLASS": "oauth2_provider.scopes.SettingsScopes",
    "READ_SCOPE": "read",
    "WRITE_SCOPE": "write",
    "OPENID_SCOPE": "id token",
    "INTROSPECTION": "introspection token",
    "AUTHORIZATION_CODE_EXPIRE_SECONDS": 60,
    "ACCESS_TOKEN_EXPIRE_SECONDS": 36000,
    "OIDC_ID_TOKEN_EXPIRE": 600,
    "REFRESH_TOKEN_EXPIRE_SECONDS": None,
    "REFRESH_TOKEN_GRACE_PERIOD_SECONDS": 0,
    "ROTATE_REFRESH_TOKEN": True,
    "ERROR_RESPONSE_WITH_SCOPES": False,
    "OIDC_SITE_URL": "http://192.168.31.62:8000",  # OPTIONAL. The OP server url.
    "OIDC_ID_TOKEN_INCLUDE_CLAIMS": False,  # OPTIONAL. If enabled, id_token will include standard claims of the user.
    "OIDC_EXTRA_SCOPE_CLAIMS": None,  # OPTIONAL. A string with the location of your class. Used to add extra scopes specific for your app.

    "APPLICATION_MODEL": APPLICATION_MODEL,
    "OIDC_APPLICATION_MODEL": OIDC_APPLICATION_MODEL,
    "ACCESS_TOKEN_MODEL": ACCESS_TOKEN_MODEL,
    "OIDC_ACCESS_TOKEN_MODEL": OIDC_ACCESS_TOKEN_MODEL,
    "GRANT_MODEL": GRANT_MODEL,
    "OIDC_GRANT_MODEL": OIDC_GRANT_MODEL,
    "REFRESH_TOKEN_MODEL": REFRESH_TOKEN_MODEL,
    "OIDC_REFRESH_TOKEN_MODEL": OIDC_REFRESH_TOKEN_MODEL,
    "OIDC_RSA_KEY_MODEL": OIDC_RSA_KEY_MODEL,
    "REQUEST_APPROVAL_PROMPT": "force",
    "ALLOWED_REDIRECT_URI_SCHEMES": ["http", "https"],

    # Special settings that will be evaluated at runtime
    "_SCOPES": [],
    "_DEFAULT_SCOPES": [],

    # Resource Server with Token Introspection
    "RESOURCE_SERVER_INTROSPECTION_URL": None,
    "RESOURCE_SERVER_AUTH_TOKEN": None,
    "RESOURCE_SERVER_INTROSPECTION_CREDENTIALS": None,
    "RESOURCE_SERVER_TOKEN_CACHING_SECONDS": 36000,

    # 登录后重定向地址所用键的名称
    "LOGIN_NEXT_PARAM_NAMES": (
        "next",
        "backPath",
        "next_path",
    ),

    # 兼容OIDC的响应类型
    "UP_COMPATIBLE_OIDC_RESPONSE_TYPE": {
        "code": "code",  # Authorization Code Flow
        "id_token": "token",  # Implicit Flow
        "id_token token": "token",  # Implicit Flow
        "code token": "code",  # Hybrid Flow
        "code id_token": "code",  # Hybrid Flow
        "code id_token token": "code"  # Hybrid Flow
    },

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
)

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    "CLIENT_ID_GENERATOR_CLASS",
    "CLIENT_SECRET_GENERATOR_CLASS",
    "OAUTH2_SERVER_CLASS",
    "OAUTH2_VALIDATOR_CLASS",
    "OAUTH2_BACKEND_CLASS",
    "SCOPES_BACKEND_CLASS",
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif "." in val:
        return import_from_string(val, setting_name)
    else:
        raise ImproperlyConfigured("Bad value for %r: %r" % (setting_name, val))


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        parts = val.split(".")
        module_path, class_name = ".".join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class OAuth2ProviderSettings(object):
    """
    A settings object, that allows OAuth2 Provider settings to be accessed as properties.

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None, mandatory=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()
        self.mandatory = mandatory or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid OAuth2Provider setting: %r" % (attr))

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
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
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        if not val and attr in self.mandatory:
            raise AttributeError("OAuth2Provider setting: %r is mandatory" % (attr))


oauth2_settings = OAuth2ProviderSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS, MANDATORY)
