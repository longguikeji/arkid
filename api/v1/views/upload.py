from arkid.core.event import dispatch_event, Event
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from arkid.core.error import ErrorCode
from arkid.core.event import SAVE_FILE
from ninja import NinjaAPI, File
from ninja.files import UploadedFile
from api.v1.schema.upload import *

@api.post("/tenant/{tenant_id}/upload/", tags=['文件上传'], auth=None)
@operation(UploadOut, use_id=True)
def upload(request, tenant_id:str, file: UploadedFile = File(...)):
    tenant = request.tenant
    data = {
        "file": file,
    }
    return dispatch_event(Event(tag=SAVE_FILE, tenant=tenant, request=request, data=data))
