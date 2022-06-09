"""
SAML2.0 协议 IDP metadata文件
"""

import os
from django.http.response import FileResponse
from django.views.decorators.cache import never_cache
from ...common.metadata import BASEDIR as MD_BASEDIR

@never_cache
def metadata(request, tenant_uuid, app_id):    # pylint: disable=unused-argument
    """
    Returns an XML with the SAML 2.0 metadata for this Idp.
    The metadata is constructed on-the-fly based on the config dict in the django settings.
    """ 
    file_path = os.path.join(MD_BASEDIR,f'{tenant_uuid}_{app_id}_idp.xml')
    response = FileResponse(open(file_path,'rb'),filename='arkid_idp.xml',as_attachment=True)
    response['Content-Type'] = 'application/octet-stream'
    return response
