from ..oneid_meta.models import User
from .oauth2_backends import get_oauthlib_core
from ..drf_expiring_authtoken.authentication import ExpiringTokenAuthentication

UserModel = User
OAuthLibCore = get_oauthlib_core()


class OAuth2Backend(ExpiringTokenAuthentication):
    """
    Authenticate against an OAuth2 access token
    """

    keyword = "bearer"
