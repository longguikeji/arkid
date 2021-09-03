"""
SAML2.0 协议 SP metadata文件
"""

from django.http.response import HttpResponse
from django.views.decorators.cache import never_cache
from six import text_type
from djangosaml2sp.sp import SP


@never_cache
def metadata(request, tenant_uuid):    # pylint: disable=unused-argument
    """
    Returns an XML with the SAML 2.0 metadata for this SP.
    The metadata is constructed on-the-fly based on the config dict in the django settings.
    """
    return HttpResponse(
        content=text_type(
            SP.metadata(tenant_uuid)
        ).encode('utf-8'),
        content_type="text/xml; charset=utf8"
    )
