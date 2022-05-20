from typing import List
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from api.v1.schema.app_protocol import AppProtocolListItemOut, AppProtocolListOut
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.models import Extension


@api.get("/tenant/{tenant_id}/app_protocols/",response=List[AppProtocolListItemOut],tags=["应用协议"],auth=None)
@operation(AppProtocolListOut)
@paginate(CustomPagination)
def get_app_protocols(request, tenant_id: str):
    """ 应用协议列表
    """
    
    extensions = Extension.active_objects.filter(type="app_protocol").all()
    
    return [
        {
            "id": item.id.hex,
            "name": item.name,
            "package": item.package
        } for item in extensions
    ]