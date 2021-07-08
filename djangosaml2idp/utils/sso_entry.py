"""
SAML2.0 SSOENTRY
"""
import logging
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from djangosaml2idp.views.SAML2IDPErrorView import SAML2IDPError as error_cbv
from .store_params_in_session import store_params_in_session
from .repr_saml import repr_saml

logger = logging.getLogger(__name__)

def sso_entry(request: HttpRequest, tenant_uuid, app_id, passed_data, binding) -> HttpResponse:
    """ Entrypoint view for SSO. Store the saml info in the request session
        and redirects to the login_process view.
    """
    try:
        store_params_in_session(request, passed_data, binding)
    except ValidationError as err:
        return error_cbv.handle_error(request, err, status_code=400)

    logger.debug("SSO requested to IDP with binding {}".format(request.session['Binding'])) # pylint: disable=logging-format-interpolation
    logger.debug("--- SAML request [\n{}] ---".format(repr_saml(request.session['SAMLRequest'], b64=True))) # pylint: disable=logging-format-interpolation

    return HttpResponseRedirect(reverse('api:saml2idp:saml_login_process', args=(tenant_uuid, app_id,)))
    