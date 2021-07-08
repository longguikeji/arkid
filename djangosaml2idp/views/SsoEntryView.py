"""
SAML2.0 SSO ENTRY
"""

import logging
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from djangosaml2idp.utils import sso_entry

logger = logging.getLogger(__name__)


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
