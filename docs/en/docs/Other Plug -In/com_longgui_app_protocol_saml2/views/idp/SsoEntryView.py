"""
SAML2.0 SSO ENTRY
"""

import logging
from django.core.exceptions import ValidationError
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
from django.utils.translation import gettext as _
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT

from arkid.config import get_app_config
from arkid.extension.models import TenantExtensionConfig
logger = logging.getLogger(__name__)


def sso_entry(request, tenant_id, config_id, passed_data, binding):
    """
    创建登陆进程
    """
    try:
        saml_request = passed_data['SAMLRequest']
    except (KeyError, MultiValueDictKeyError) as err:
        raise ValidationError(_('not a valid SAMLRequest: {}').format(repr(err))) # pylint: disable=raise-missing-from
    
    tenantextensionconfig = TenantExtensionConfig.valid_objects.get(id=config_id)

    request.session['Binding'] = binding
    request.session['SAMLRequest'] = saml_request
    request.session['RelayState'] = passed_data.get('RelayState', '')
    return HttpResponseRedirect(get_app_config().get_host()+reverse(f'{tenantextensionconfig.config["namespace"]}:idp_login_process', args=(tenant_id, config_id)))


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class SSOEntry(View):
    """ SSO entry
    """

    def get(self, request, tenant_id, config_id):
        """ GET 方法
        """
        passed_data = request.GET
        binding = BINDING_HTTP_REDIRECT
        return sso_entry(request, tenant_id, config_id, passed_data, binding)

    def post(self, request, tenant_id, config_id):
        """ POST 方法
        """
        passed_data = request.POST
        binding = BINDING_HTTP_POST
        return sso_entry(request, tenant_id, config_id, passed_data, binding)
