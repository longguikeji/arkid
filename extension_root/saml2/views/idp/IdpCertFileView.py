"""
SAML2.0 协议 IDP cert文件
"""

import os
from django.http.response import FileResponse
from django.views.decorators.cache import never_cache
from ...common.certs import BASEDIR,check_self_signed_cert

@never_cache
def cert(request, tenant_uuid):  
    file_path = os.path.join(BASEDIR,f'{tenant_uuid}.crt')
    check_self_signed_cert(tenant_uuid)
    response = FileResponse(open(file_path,'rb'),filename='idp.crt',as_attachment=True)
    response['Content-Type'] = 'application/octet-stream'
    return response
