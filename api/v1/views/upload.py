from arkid.core.constants import *
from arkid.core.event import dispatch_event, Event
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.error import ErrorCode, ErrorDict, SuccessDict
from arkid.core.event import SAVE_FILE
from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from api.v1.schema.upload import *
from arkid.extension.models import Extension

@api.post("/tenant/{tenant_id}/upload/",response=UploadOut, tags=['文件上传'])
@operation(UploadOut, use_id=True,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
def upload(request, tenant_id:str, file: UploadedFile = File(...)):
    tenant = request.tenant
    data = {
        "file": file,
    }
    
    extension = Extension.active_objects.filter(
        type="storage"
    ).first()
    responses = dispatch_event(Event(tag=SAVE_FILE, tenant=tenant, request=request, packages=extension.package, data=data))
    if not responses:
        return ErrorDict(ErrorCode.STORAGE_NOT_EXISTS)
    useless, (data, extension) = responses[0]
    
    if not data:
        return ErrorDict(ErrorCode.STORAGE_FAILED)
    
    return SuccessDict(
        {
            "url":data
        }
    )