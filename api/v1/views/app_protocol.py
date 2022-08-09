from typing import List
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.translation import gettext_default as _
from api.v1.schema.app_protocol import AppProtocolListItemOut, AppProtocolListOut
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.core.models import Extension
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.config import get_app_config

@api.get("/tenant/{tenant_id}/app_protocols/",response=List[AppProtocolListItemOut],tags=["应用协议"])
@operation(AppProtocolListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
@paginate(CustomPagination)
def get_app_protocols(request, tenant_id: str):
    """ 应用协议列表
    """
    rs = []
    host = get_app_config().get_frontend_host()
    # 拿到默认的系统插件
    qs = Extension.valid_objects.all()
    packages = []
    for item in qs:
        ext_dir = item.ext_dir
        package = item.package
        if 'extension_root' in ext_dir and package not in packages:
            packages.append(package)
    # 插件筛选
    for k,v in AppProtocolExtension.composite_schema_map.items():
        for p_k,p_v in v.items():
            if p_k in packages:
                rs.append({
                    "name": k,
                    "doc_url": f"{host}/docs/%20%20系统插件/{p_k.replace('.','_')}/",
                    "package": p_k
                })
            else:
                rs.append({
                    "name": k,
                    "doc_url": f"{host}/docs/%20其它插件/{p_k.replace('.','_')}/",
                    "package": p_k
                })
    return rs