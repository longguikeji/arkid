from datetime import timedelta
from urllib.parse import parse_qsl, urlparse

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from jwkest.jwk import SYMKey
from jwkest.jws import JWS
from Cryptodome.PublicKey.RSA import importKey
from jwkest.jwk import RSAKey

from ..oauth2_provider.generators import generate_client_id, generate_client_secret
from ..oauth2_provider.scopes import get_scopes_backend
from ..oauth2_provider.settings import oauth2_settings
from ..oauth2_provider.validators import RedirectURIValidator, WildcardSet

from hashlib import sha256, md5
import json
import base64
import binascii


class AbstractApplication(models.Model):
    """
    An Application instance represents a Client on the Authorization server.
    Usually an Application is created manually by client's developers after
    logging in on an Authorization Server.

    Fields:

    * :attr:`client_id` The client identifier issued to the client during the
                        registration process as described in :rfc:`2.2`
    * :attr:`user` ref to a Django user
    * :attr:`redirect_uris` The list of allowed redirect uri. The string
                            consists of valid URLs separated by space
    * :attr:`client_type` Client type as described in :rfc:`2.1`
    * :attr:`authorization_grant_type` Authorization flows available to the
                                       Application
    * :attr:`client_secret` Confidential secret issued to the client during
                            the registration process as described in :rfc:`2.2`
    * :attr:`name` Friendly name for the Application
    """
    CLIENT_CONFIDENTIAL = "confidential"
    CLIENT_PUBLIC = "public"
    CLIENT_TYPES = (
        (CLIENT_CONFIDENTIAL, _("Confidential")),
        (CLIENT_PUBLIC, _("Public")),
    )

    GRANT_AUTHORIZATION_CODE = "authorization-code"
    GRANT_IMPLICIT = "implicit"
    GRANT_PASSWORD = "password"
    GRANT_CLIENT_CREDENTIALS = "client-credentials"
    GRANT_TYPES = (
        (GRANT_AUTHORIZATION_CODE, _("Authorization code")),
        (GRANT_IMPLICIT, _("Implicit")),
        (GRANT_PASSWORD, _("Resource owner password-based")),
        (GRANT_CLIENT_CREDENTIALS, _("Client credentials")),
    )

    id = models.BigAutoField(primary_key=True)
    client_id = models.CharField(max_length=100, unique=True, default=generate_client_id, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="%(app_label)s_%(class)s",
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    redirect_uris = models.TextField(
        blank=True,
        help_text=_("Allowed URIs list, space separated"),
    )
    client_type = models.CharField(max_length=32, choices=CLIENT_TYPES, default=CLIENT_CONFIDENTIAL)
    authorization_grant_type = models.CharField(
        max_length=32,
        choices=GRANT_TYPES,
        default=GRANT_AUTHORIZATION_CODE,
    )
    client_secret = models.CharField(max_length=255, blank=True, default=generate_client_secret, db_index=True)
    name = models.CharField(max_length=255, blank=True)
    skip_authorization = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name or self.client_id

    @property
    def default_redirect_uri(self):
        """
        Returns the default redirect_uri extracting the first item from
        the :attr:`redirect_uris` string
        """
        if self.redirect_uris:
            return self.redirect_uris.split().pop(0)

        assert False, ("If you are using implicit, authorization_code"
                       "or all-in-one grant_type, you must define "
                       "redirect_uris field in your Application model")

    def redirect_uri_allowed(self, uri):
        """
        Checks if given url is one of the items in :attr:`redirect_uris` string

        :param uri: Url to check
        """
        parsed_uri = urlparse(uri)
        uqs_set = set(parse_qsl(parsed_uri.query))
        for allowed_uri in self.redirect_uris.split():
            parsed_allowed_uri = urlparse(allowed_uri)

            if (parsed_allowed_uri.scheme == parsed_uri.scheme and parsed_allowed_uri.netloc == parsed_uri.netloc
                    and parsed_allowed_uri.path == parsed_uri.path):

                aqs_set = set(parse_qsl(parsed_allowed_uri.query))

                if aqs_set.issubset(uqs_set):
                    return True

        return False

    def clean(self):
        from django.core.exceptions import ValidationError

        grant_types = (
            AbstractApplication.GRANT_AUTHORIZATION_CODE,
            AbstractApplication.GRANT_IMPLICIT,
        )

        redirect_uris = self.redirect_uris.strip().split()
        allowed_schemes = set(s.lower() for s in self.get_allowed_schemes())

        if redirect_uris:
            validator = RedirectURIValidator(WildcardSet())
            for uri in redirect_uris:
                validator(uri)
                scheme = urlparse(uri).scheme
                if scheme not in allowed_schemes:
                    raise ValidationError(_("Unauthorized redirect scheme: {scheme}").format(scheme=scheme))

        elif self.authorization_grant_type in grant_types:
            raise ValidationError(
                _("redirect_uris cannot be empty with grant_type {grant_type}").format(
                    grant_type=self.authorization_grant_type))

    def get_absolute_url(self):
        return reverse("oauth2_provider:detail", args=[str(self.id)])

    def get_allowed_schemes(self):
        """
        Returns the list of redirect schemes allowed by the Application.
        By default, returns `ALLOWED_REDIRECT_URI_SCHEMES`.
        """
        return oauth2_settings.ALLOWED_REDIRECT_URI_SCHEMES

    def allows_grant_type(self, *grant_types):
        return self.authorization_grant_type in grant_types

    def is_usable(self, request):
        """
        Determines whether the application can be used.

        :param request: The HTTP request being processed.
        """
        return True


class ApplicationManager(models.Manager):
    def get_by_natural_key(self, client_id):
        return self.get(client_id=client_id)


class OidcApplication(models.Model):

    JWT_ALG_HS256 = 'HS256'
    JWT_ALG_RS256 = 'RS256'
    JWT_ALGS = (
        (JWT_ALG_HS256, _('HS256')),
        (JWT_ALG_RS256, _('RS256')),
    )

    CLIENT_CONFIDENTIAL = "confidential"
    CLIENT_PUBLIC = "public"
    CLIENT_TYPES = (
        (CLIENT_CONFIDENTIAL, _("Confidential")),
        (CLIENT_PUBLIC, _("Public")),
    )
    CODE = 'code'
    IDTOKEN = 'id_token'
    IDTOKEN_TOKEN = 'id_token token'
    CODE_TOKEN = 'code token'
    CODE_IDTOKEN = 'code id_token'
    CODE_IDTOKEN_TOKEN = 'code id_token token'
    RESPONSE_TYPES = [
        (CODE, _('code (Authorization Code Flow)')),
        (IDTOKEN, _('id_token (Implicit Flow)')),
        (IDTOKEN_TOKEN, _('id_token token (Implicit Flow)')),
        (CODE_TOKEN, _('code token (Hybrid Flow)')),
        (CODE_IDTOKEN, _('code id_token (Hybrid Flow)')),
        (CODE_IDTOKEN_TOKEN, _('code id_token token (Hybrid Flow)')),
    ]
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, default='')
    # owner = models.ForeignKey(
    #     settings.AUTH_USER_MODEL, verbose_name=_(u'Owner'), blank=True,
    #     null=True, default=None, on_delete=models.SET_NULL, related_name='oidc_clients_set')
    client_type = models.CharField(
        max_length=30,
        choices=CLIENT_TYPES,
        default=CLIENT_CONFIDENTIAL,
        verbose_name=_(u'Client Type'),
        help_text=_(u'<b>Confidential</b> clients are capable of maintaining the confidentiality'
                    u' of their credentials. <b>Public</b> clients are incapable.'))
    client_id = models.CharField(max_length=255, unique=True, default=generate_client_id)
    client_secret = models.CharField(max_length=255, blank=True, default=generate_client_secret)
    # response_types = models.ManyToManyField(ResponseType)
    response_type = models.CharField(
        max_length=32,
        choices=RESPONSE_TYPES,
        default=CODE,
    )
    jwt_alg = models.CharField(
        max_length=10,
        choices=JWT_ALGS,
        default=JWT_ALG_RS256,
        help_text=_(u'Algorithm used to encode ID Tokens.'))
    date_created = models.DateField(auto_now_add=True)
    website_url = models.CharField(
        max_length=255, blank=True, default='')
    terms_url = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text=_(u'External reference to the privacy policy of the client.'))
    contact_email = models.CharField(
        max_length=255, blank=True, default='')
    logo = models.FileField(
        blank=True, default='', upload_to='oidc_provider/clients')
    reuse_consent = models.BooleanField(
        default=True,
        help_text=_('If enabled, server will save the user consent given to a specific client, '
                    'so that user won\'t be prompted for the same authorization multiple times.'))
    require_consent = models.BooleanField(
        default=True,
        help_text=_('If disabled, the Server will NEVER ask the user for consent.'))
    # _redirect_uris = models.TextField(
    #     default='', verbose_name=_(u'Redirect URIs'),
    #     help_text=_(u'Enter each URI on a new line.'))
    redirect_uris = models.TextField(default='', help_text=_(u'Enter each URI on a new line.'))
    _post_logout_redirect_uris = models.TextField(
        blank=True,
        default='',
        help_text=_(u'Enter each URI on a new line.'))
    _scope = models.TextField(
        blank=True,
        default='',
        help_text=_('Specifies the authorized scope values for the client app.'))

    skip_authorization = models.BooleanField(default=False)

    user = models.ForeignKey('oneid_meta.User',
                             related_name="%(app_label)s_%(class)s",
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    app = models.OneToOneField('oneid_meta.APP',
                               related_name="oidc_app",
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)

    class Meta:
        abstract = False
        swappable = "OAUTH2_PROVIDER_OIDC_APPLICATION_MODEL"

    objects = ApplicationManager()

    def __str__(self):
        return self.name or self.client_id

    # def __unicode__(self):
    #     return self.__str__()

    def natural_key(self):
        return (self.client_id, )

    def response_type_values(self):
        return self.response_type

    def response_type_descriptions(self):
        # return as a list, rather than a generator, so descriptions display correctly in admin
        # return [response_type.description for response_type in self.response_types.all()]
        return '忽略了response type的描述'

    # @property
    # def redirect_uris(self):
    #     return self.redirect_uris.splitlines()
    #
    # @redirect_uris.setter
    # def redirect_uris(self, value):
    #     self.redirect_uris = '\n'.join(value)

    @property
    def post_logout_redirect_uris(self):
        return self._post_logout_redirect_uris.splitlines()

    @post_logout_redirect_uris.setter
    def post_logout_redirect_uris(self, value):
        self._post_logout_redirect_uris = '\n'.join(value)

    @property
    def scope(self):
        return self._scope.split()

    @scope.setter
    def scope(self, value):
        self._scope = ' '.join(value)

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0] if self.redirect_uris else ''

    def is_usable(self, request):
        """
        Determines whether the application can be used.

        :param request: The HTTP request being processed.
        """
        return True

    def redirect_uri_allowed(self, uri):
        """
        Checks if given url is one of the items in :attr:`redirect_uris` string
        :param uri: Url to check
        """
        parsed_uri = urlparse(uri)
        uqs_set = set(parse_qsl(parsed_uri.query))
        for allowed_uri in self.redirect_uris.split():
            parsed_allowed_uri = urlparse(allowed_uri)

            if (parsed_allowed_uri.scheme == parsed_uri.scheme and parsed_allowed_uri.netloc == parsed_uri.netloc
                    and parsed_allowed_uri.path == parsed_uri.path):

                aqs_set = set(parse_qsl(parsed_allowed_uri.query))

                if aqs_set.issubset(uqs_set):
                    return True

        return False

    def allows_grant_type(self, *grant_types):
        return self.response_type in grant_types

    def get_allowed_schemes(self):
        """
        Returns the list of redirect schemes allowed by the Application.
        By default, returns `ALLOWED_REDIRECT_URI_SCHEMES`.
        """
        return oauth2_settings.ALLOWED_REDIRECT_URI_SCHEMES


class Application(AbstractApplication):

    user = models.ForeignKey('oneid_meta.User',
                             related_name="%(app_label)s_%(class)s",
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    app = models.OneToOneField('oneid_meta.APP',
                               related_name="oauth_app",
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)

    objects = ApplicationManager()

    class Meta(AbstractApplication.Meta):
        swappable = "OAUTH2_PROVIDER_APPLICATION_MODEL"

    def natural_key(self):
        return (self.client_id, )

    @property
    def more_detail(self):
        return [{
            'name': '认证地址',
            'key': 'auth_url',
            'value': settings.BASE_URL + '/oauth/authorize/',
        }, {
            'name': '获取token地址',
            'key': 'token_url',
            'value': settings.BASE_URL + '/oauth/token/',
        }, {
            'name': '身份信息地址',
            'key': 'profile_url',
            'value': settings.BASE_URL + '/oauth/userinfo/'
        }]


class AbstractGrant(models.Model):
    """
    A Grant instance represents a token with a short lifetime that can
    be swapped for an access token, as described in :rfc:`4.1.2`

    Fields:

    * :attr:`user` The Django user who requested the grant
    * :attr:`code` The authorization code generated by the authorization server
    * :attr:`application` Application instance this grant was asked for
    * :attr:`expires` Expire time in seconds, defaults to
                      :data:`settings.AUTHORIZATION_CODE_EXPIRE_SECONDS`
    * :attr:`redirect_uri` Self explained
    * :attr:`scope` Required scopes, optional
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s")
    code = models.CharField(max_length=255, unique=True)    # code comes from oauthlib
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, on_delete=models.CASCADE)
    expires = models.DateTimeField()
    redirect_uri = models.CharField(max_length=255)
    scope = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires

    def redirect_uri_allowed(self, uri):
        return uri == self.redirect_uri

    def __str__(self):
        return self.code

    class Meta:
        abstract = True


class Grant(AbstractGrant):

    user = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s")

    class Meta(AbstractGrant.Meta):
        swappable = "OAUTH2_PROVIDER_GRANT_MODEL"


class OidcGrant(AbstractGrant):

    CODE_CHALLENGE_METHODS = [
        ('plain', _('plain coded format')),
        ('S256', _('S256 coded format')),
    ]

    application = models.ForeignKey(oauth2_settings.OIDC_APPLICATION_MODEL, on_delete=models.CASCADE)
    user = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s")

    nonce = models.CharField(max_length=255, blank=True, default='', verbose_name=_(u'Nonce'))
    code_challenge = models.CharField(max_length=255, null=True, verbose_name=_(u'Code Challenge'))
    code_challenge_method = models.CharField(choices=CODE_CHALLENGE_METHODS, max_length=255, null=True,
                                             verbose_name=_(u'Code Challenge Method'))

    class Meta(AbstractGrant.Meta):
        swappable = "OAUTH2_PROVIDER_OIDC_GRANT_MODEL"
        abstract = False


class AbstractAccessToken(models.Model):
    """
    An AccessToken instance represents the actual access token to
    access user's resources, as in :rfc:`5`.

    Fields:

    * :attr:`user` The Django user representing resources' owner
    * :attr:`source_refresh_token` If from a refresh, the consumed RefeshToken
    * :attr:`token` Access token
    * :attr:`application` Application instance
    * :attr:`expires` Date and time of token expiration, in DateTime format
    * :attr:`scope` Allowed scopes
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             related_name="%(app_label)s_%(class)s")
    source_refresh_token = models.OneToOneField(
    # unique=True implied by the OneToOneField
        oauth2_settings.REFRESH_TOKEN_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="refreshed_access_token")
    token = models.CharField(
        max_length=255,
        unique=True,
    )
    application = models.ForeignKey(
        oauth2_settings.APPLICATION_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    expires = models.DateTimeField()
    scope = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_valid(self, scopes=None):
        """
        Checks if the access token is valid.

        :param scopes: An iterable containing the scopes to check or None
        """
        return not self.is_expired() and self.allow_scopes(scopes)

    def is_expired(self):
        """
        Check token expiration with timezone awareness
        """
        if not self.expires:
            return True

        return timezone.now() >= self.expires

    def allow_scopes(self, scopes):
        """
        Check if the token allows the provided scopes

        :param scopes: An iterable containing the scopes to check
        """
        if not scopes:
            return True

        provided_scopes = set(self.scope.split())
        resource_scopes = set(scopes)
        return resource_scopes.issubset(provided_scopes)

    def revoke(self):
        """
        Convenience method to uniform tokens' interface, for now
        simply remove this token from the database in order to revoke it.
        """
        self.delete()

    @property
    def scopes(self):
        """
        Returns a dictionary of allowed scope names (as keys) with their descriptions (as values)
        """
        all_scopes = get_scopes_backend().get_all_scopes()
        token_scopes = self.scope.split()
        return {name: desc for name, desc in all_scopes.items() if name in token_scopes}

    def __str__(self):
        return self.token

    class Meta:
        abstract = True


class AccessToken(AbstractAccessToken):

    user = models.ForeignKey('oneid_meta.User',
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             related_name="%(app_label)s_%(class)s")

    class Meta(AbstractAccessToken.Meta):
        swappable = "OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL"


class OidcAccessToken(AbstractAccessToken):

    source_refresh_token = models.OneToOneField(
    # unique=True implied by the OneToOneField
        oauth2_settings.OIDC_REFRESH_TOKEN_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="refreshed_access_token")

    application = models.ForeignKey(
        oauth2_settings.OIDC_APPLICATION_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    id_token = models.TextField(verbose_name=_(u'ID Token'), null=False)
    user = models.ForeignKey('oneid_meta.User',
                             on_delete=models.CASCADE,
                             blank=True,
                             null=True,
                             related_name="%(app_label)s_%(class)s")

    class Meta(AbstractAccessToken.Meta):
        abstract = False
        swappable = "OAUTH2_PROVIDER_OIDC_ACCESS_TOKEN_MODEL"

    @property
    def _id_token(self):
        return json.loads(self.id_token) if self.id_token else None

    @_id_token.setter
    def _id_token(self, value):
        self.id_token = json.dumps(value)

    @property
    def at_hash(self):
        # @@@ d-o-p only supports 256 bits (change this if that changes)
        hashed_access_token = sha256(
            self.token.encode('ascii')
        ).hexdigest().encode('ascii')
        return base64.urlsafe_b64encode(
            binascii.unhexlify(
                hashed_access_token[:len(hashed_access_token) // 2]
            )
        ).rstrip(b'=').decode('ascii')

    @classmethod
    def encode_id_token(cls, payload, client):
        """
        Represent the ID Token as a JSON Web Token (JWT).
        Return a hash.
        """
        keys = cls.get_client_alg_keys(client)
        _jws = JWS(payload, alg=client.jwt_alg)
        return _jws.sign_compact(keys)

    @classmethod
    def get_client_alg_keys(cls, client):
        """
        Takes a client and returns the set of keys associated with it.
        Returns a list of keys.
        """
        if client.jwt_alg == 'RS256':
            keys = []
            for rsa_key in get_oidc_rsa_key_model().objects.all():
                keys.append(RSAKey(key=importKey(rsa_key.key), kid=rsa_key.kid))
            if not keys:
                raise Exception('You must add at least one RSA Key.')
        elif client.jwt_alg == 'HS256':
            keys = [SYMKey(key=client.client_secret, alg=client.jwt_alg)]
        else:
            raise Exception('Unsupported key algorithm.')
        return keys


class AbstractRefreshToken(models.Model):
    """
    A RefreshToken instance represents a token that can be swapped for a new
    access token when it expires.

    Fields:

    * :attr:`user` The Django user representing resources' owner
    * :attr:`token` Token value
    * :attr:`application` Application instance
    * :attr:`access_token` AccessToken instance this refresh token is
                           bounded to
    * :attr:`revoked` Timestamp of when this refresh token was revoked
    """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s")
    token = models.CharField(max_length=255)
    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, on_delete=models.CASCADE)
    access_token = models.OneToOneField(oauth2_settings.ACCESS_TOKEN_MODEL,
                                        on_delete=models.SET_NULL,
                                        blank=True,
                                        null=True,
                                        related_name="refresh_token")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    revoked = models.DateTimeField(null=True)

    def revoke(self):
        """
        Mark this refresh token revoked and revoke related access token
        """
        access_token_model = get_access_token_model()
        refresh_token_model = get_refresh_token_model()
        with transaction.atomic():
            self = refresh_token_model.objects.filter(pk=self.pk, revoked__isnull=True).select_for_update().first()
            if not self:
                return

            try:
                access_token_model.objects.get(id=self.access_token_id).revoke()
            except access_token_model.DoesNotExist:
                pass
            self.access_token = None
            self.revoked = timezone.now()
            self.save()

    def __str__(self):
        return self.token

    class Meta:
        abstract = True
        unique_together = (
            "token",
            "revoked",
        )


class RefreshToken(AbstractRefreshToken):
    user = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s")

    class Meta(AbstractRefreshToken.Meta):
        swappable = "OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL"


class OidcRefreshToken(AbstractRefreshToken):
    access_token = models.OneToOneField(oauth2_settings.OIDC_ACCESS_TOKEN_MODEL,
                                        on_delete=models.SET_NULL,
                                        blank=True,
                                        null=True,
                                        related_name="refresh_token")

    application = models.ForeignKey(oauth2_settings.OIDC_APPLICATION_MODEL, on_delete=models.CASCADE)
    user = models.ForeignKey('oneid_meta.User', on_delete=models.CASCADE, related_name="%(app_label)s_%(class)s")

    class Meta(AbstractRefreshToken.Meta):
        swappable = "OAUTH2_PROVIDER_OIDC_REFRESH_TOKEN_MODEL"
        abstract = False


class OidcRsaKey(models.Model):

    key = models.TextField(
        verbose_name=_(u'Key'), help_text=_(u'Paste your private RSA Key here.'))

    class Meta:
        verbose_name = _(u'RSA Key')
        verbose_name_plural = _(u'RSA Keys')
        swappable = 'OAUTH2_PROVIDER_OIDC_RSA_KEY'

    def __str__(self):
        return u'{0}'.format(self.kid)

    def __unicode__(self):
        return self.__str__()

    @property
    def kid(self):
        return u'{0}'.format(md5(self.key.encode('utf-8')).hexdigest() if self.key else '')


def get_application_model():
    """ Return the Application model that is active in this project. """
    return apps.get_model(oauth2_settings.APPLICATION_MODEL)


def get_oidc_application_model():
    """ Return the OIDC Application model that is active in this project. """
    return apps.get_model(oauth2_settings.OIDC_APPLICATION_MODEL)


def get_grant_model():
    """ Return the Grant model that is active in this project. """
    return apps.get_model(oauth2_settings.GRANT_MODEL)


def get_oidc_grant_model():
    """ Return the OIDC Grant model that is active in this project. """
    return apps.get_model(oauth2_settings.OIDC_GRANT_MODEL)


def get_access_token_model():
    """ Return the AccessToken model that is active in this project. """
    return apps.get_model(oauth2_settings.ACCESS_TOKEN_MODEL)


def get_oidc_access_token_model():
    """ Return the OIDC AccessToken model that is active in this project. """
    return apps.get_model(oauth2_settings.OIDC_ACCESS_TOKEN_MODEL)


def get_refresh_token_model():
    """ Return the RefreshToken model that is active in this project. """
    return apps.get_model(oauth2_settings.REFRESH_TOKEN_MODEL)


def get_oidc_refresh_token_model():
    """ Return the OIDC RefreshToken model that is active in this project. """
    return apps.get_model(oauth2_settings.OIDC_REFRESH_TOKEN_MODEL)


def get_oidc_rsa_key_model():
    """ Return the OIDC RSAKey model that is active in this project. """
    return apps.get_model(oauth2_settings.OIDC_RSA_KEY_MODEL)


def clear_expired():
    now = timezone.now()
    refresh_expire_at = None
    access_token_model = get_access_token_model()
    refresh_token_model = get_refresh_token_model()
    grant_model = get_grant_model()
    REFRESH_TOKEN_EXPIRE_SECONDS = oauth2_settings.REFRESH_TOKEN_EXPIRE_SECONDS
    if REFRESH_TOKEN_EXPIRE_SECONDS:
        if not isinstance(REFRESH_TOKEN_EXPIRE_SECONDS, timedelta):
            try:
                REFRESH_TOKEN_EXPIRE_SECONDS = timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)
            except TypeError:
                e = "REFRESH_TOKEN_EXPIRE_SECONDS must be either a timedelta or seconds"
                raise ImproperlyConfigured(e)
        refresh_expire_at = now - REFRESH_TOKEN_EXPIRE_SECONDS

    with transaction.atomic():
        if refresh_expire_at:
            refresh_token_model.objects.filter(revoked__lt=refresh_expire_at).delete()
            refresh_token_model.objects.filter(access_token__expires__lt=refresh_expire_at).delete()
        access_token_model.objects.filter(refresh_token__isnull=True, expires__lt=now).delete()
        grant_model.objects.filter(expires__lt=now).delete()
