"""
SAML2.0 SSO ENTRY
"""

import logging
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
logger = logging.getLogger(__name__)

def sso_entry(request, tenant_uuid, app_id, passed_data, binding):
    try:
        saml_request = passed_data['SAMLRequest']
    except (KeyError, MultiValueDictKeyError) as e:
        raise ValidationError(_('not a valid SAMLRequest: {}').format(repr(e)))

    request.session['Binding'] = binding
    request.session['SAMLRequest'] = saml_request
    request.session['RelayState'] = passed_data.get('RelayState', '')
    return HttpResponseRedirect(reverse('api:saml2idp:saml_login_process',args=(tenant_uuid,app_id)))


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class SSOEntry(View):
    """ SSO entry
    """

    def get(self, request, tenant_uuid, app_id):
        """ GET 方法
        """
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT
        return sso_entry(request, tenant_uuid, app_id, passed_data, binding)

    def post(self, request, tenant_uuid, app_id):
        """ POST 方法
        """
        passed_data = request.GET
        binding = BINDING_HTTP_POST
        return sso_entry(request, tenant_uuid, app_id, passed_data, binding)
