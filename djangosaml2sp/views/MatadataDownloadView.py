"""
SAML2.0协议 SP元文件下载
"""

from django.views.decorators.cache import never_cache
from .MetadataView import metadata


@never_cache
def download_metadata(request, tenant_uuid):    # pylint: disable=unused-argument
    """
    Returns an XML with the SAML 2.0 metadata for this SP.
    The metadata is constructed on-the-fly based on the config dict in the django settings.
    """
    res = metadata(request, tenant_uuid)
    res['Content-Type'] = 'application/octet-stream'
    res['Content-Disposition'] = 'attachment;filename="SP_metadata.xml"'
    return res
