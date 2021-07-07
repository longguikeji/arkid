from typing import Reversible
from djangosaml2idp.utils import repr_saml
import logging
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views import View
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from django.shortcuts import reverse
from .SAML2IDPErrorView import SAML2IDPError as error_cbv

logger = logging.getLogger(__name__)

class SSOEntry(View):

    def get(self,request,tenant_uuid,*argc,**kwargs):
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT
        return self.sso_entry(request,tenant_uuid,passed_data,binding)

    def post(self,request,tenant_uuid,*argc,**kwargs):
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT
        return self.sso_entry(request,tenant_uuid,passed_data,binding)


    def store_params_in_session(self, request: HttpRequest, passed_data, binding) -> None:
        """ Gathers the SAML parameters from the HTTP request and store them in the session
        """
        try:
            saml_request = passed_data['SAMLRequest']
        except (KeyError, MultiValueDictKeyError) as e:
            raise ValidationError(_('not a valid SAMLRequest: {}').format(repr(e)))

        request.session['Binding'] = binding
        request.session['SAMLRequest'] = saml_request
        request.session['RelayState'] = passed_data.get('RelayState', '')

    def sso_entry(self, request: HttpRequest, tenant_uuid, passed_data, binding, *args, **kwargs) -> HttpResponse:
        """ Entrypoint view for SSO. Store the saml info in the request session
            and redirects to the login_process view.
        """
        try:
            self.store_params_in_session(request,passed_data,binding)
        except ValidationError as e:
            return error_cbv.handle_error(request, e, status_code=400)

        logger.debug("SSO requested to IDP with binding {}".format(request.session['Binding']))
        logger.debug("--- SAML request [\n{}] ---".format(repr_saml(request.session['SAMLRequest'], b64=True)))

        return HttpResponseRedirect(reverse('api:saml2idp:saml_login_process',args=(tenant_uuid,)))
    

    
