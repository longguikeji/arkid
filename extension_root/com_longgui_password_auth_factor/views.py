from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.error import ErrorCode
from .schema import *

@api.get(
    "/tenant/{tenant_id}/mine_password/",
    tags=["密码认证"],
    auth=None,
    response=MinePasswordOut,
)
def get_mine_password(request, tenant_id: str):
    """获取密码,TODO
    """
    return {
        "data": {
            "password": "",
            "confirm_password": ""
        }
    }
    
@api.post(
    "/tenant/{tenant_id}/mine_password/",
    tags=["密码认证"],
    auth=None,
    response=UpdateMinePasswordOut,
)
def update_mine_password(request, tenant_id: str,data:UpdateMinePasswordIn):
    """更改密码,TODO
    """
    
    return {'error': ErrorCode.OK.value}