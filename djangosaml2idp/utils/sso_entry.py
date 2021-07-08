import logging
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views import View
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.shortcuts import reverse

from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from djangosaml2idp.utils import sso_entry
from djangosaml2idp.views.SAML2IDPErrorView import SAML2IDPError as error_cbv
from .store_params_in_session import store_params_in_session

logger = logging.getLogger(__name__)

def sso_entry(self, request: HttpRequest, tenant_uuid, app_id, passed_data, binding, *args, **kwargs) -> HttpResponse:
    """ Entrypoint view for SSO. Store the saml info in the request session
        and redirects to the login_process view.
    """
    try:
        store_params_in_session(request, passed_data, binding)
    except ValidationError as e:
        return error_cbv.handle_error(request, e, status_code=400)

    logger.debug("SSO requested to IDP with binding {}".format(
        request.session['Binding']))
    logger.debug(
        "--- SAML request [\n{}] ---".format(repr_saml(request.session['SAMLRequest'], b64=True)))

    return HttpResponseRedirect(reverse('api:saml2idp:saml_login_process', args=(tenant_uuid, app_id,)))