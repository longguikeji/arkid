"""
SAML2.0 协议 IDP metadata文件
"""

from django.http.response import HttpResponse
from django.views.decorators.cache import never_cache
from saml2.config import IdPConfig
from saml2.metadata import entity_descriptor
from six import text_type
from djangosaml2idp import idpsettings

@never_cache
def metadata(request, tenant_uuid, app_id):    # pylint: disable=unused-argument
    """
    Returns an XML with the SAML 2.0 metadata for this Idp.
    The metadata is constructed on-the-fly based on the config dict in the django settings.
    """
    conf = IdPConfig()
    conf.load(idpsettings.get_saml_idp_config(tenant_uuid, app_id))
    meta_data = entity_descriptor(conf)
    return HttpResponse(content=text_type(meta_data).encode('utf-8'), content_type="text/xml; charset=utf8")
