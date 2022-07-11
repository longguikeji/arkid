from typing import List
from arkid.core.api import api, operation
from arkid.core.translation import gettext_default as _
from api.v1.schema.app_protocol import AppProtocolListItemOut, AppProtocolListOut
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.models import Extension
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.config import get_app_config


@api.get("/tenant/{tenant_id}/app_protocols/",response=List[AppProtocolListItemOut],tags=["应用协议"])
@operation(AppProtocolListOut)
@paginate(CustomPagination)
def get_app_protocols(request, tenant_id: str):
    """ 应用协议列表
    """
    rs = []
    host = get_app_config().get_frontend_host()
    for k,v in AppProtocolExtension.composite_schema_map.items():
        for p_k,p_v in v.items():
            rs.append({
                "name": k,
                "doc_url": f"{host}/arkid/%20系统插件/{p_k.replace('.','_')}/",
                "package": p_k
            })
    
    return rs