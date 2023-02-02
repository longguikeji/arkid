import logging
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse, NoReverseMatch

from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes

from .services import service_allowed


logger = logging.getLogger(__name__)


def add_query_params(url, params):
    """
    Inject additional query parameters into an existing URL. If
    parameters already exist with the same name, they will be
    overwritten. Parameters with empty values are ignored. Return
    the modified URL as a string.
    """
    def encode(s):
        return force_bytes(s, settings.DEFAULT_CHARSET)
    params = dict([(encode(k), encode(v)) for k, v in params.items() if v])

    parts = list(urlparse(url))
    query = dict(parse_qsl(parts[4]))
    query.update(params)
    parts[4] = urlencode(query)
    return urlunparse(parts)


def is_scheme_https(url):
    """
    Test the scheme of the parameter URL to see if it is HTTPS. If
    it is HTTPS return ``True``, otherwise return ``False``.
    """
    return 'https' == urlparse(url).scheme


def clean_service_url(url):
    """
    Return only the scheme, hostname (with optional port) and path
    components of the parameter URL.
    """
    parts = urlparse(url)
    return urlunparse((parts.scheme, parts.netloc, parts.path, '', '', ''))


def match_service(service1, service2):
    """
    Compare two service URLs. Return ``True`` if the scheme, hostname,
    optional port and path match.
    """
    s1, s2 = urlparse(service1), urlparse(service2)
    try:
        return (s1.scheme, s1.netloc, s1.path) == (s2.scheme, s2.netloc, s2.path)
    except ValueError:
        return False


def redirect(to, *args, **kwargs):
    """
    Similar to the Django ``redirect`` shortcut but with altered
    functionality. If an optional ``params`` argument is provided, the
    dictionary items will be injected as query parameters on the
    redirection URL.
    """
    params = kwargs.pop('params', {})
    try:
        to = reverse(to, args=args, kwargs=kwargs)
    except NoReverseMatch:
        if '/' not in to and '.' not in to:
            to = reverse('cas_login')
        elif not service_allowed(to):
            raise PermissionDenied()

    if params:
        to = add_query_params(to, params)

    logger.debug("Redirecting to %s" % to)
    return HttpResponseRedirect(to)


def to_bool(str):
    """
    Converts a given string to a boolean value. Leading and trailing
    whitespace is ignored, so strings of whitespace are evaluated as
    ``False``.
    """
    if str:
        return bool(str.strip())
    return False
