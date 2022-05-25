from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.error import ErrorCode
from .schema import *

@api.get(
    "/tenant/{tenant_id}/mine_mobile/",
    tags=["手机验证码认证"],
    auth=None,
    response=MineMobileOut,
)
def get_mine_mobile(request, tenant_id: str):
    """获取手机号码,TODO
    """
    
    return {
        "data": {
            "mobile": ""
        }
    }
    
@api.post(
    "/tenant/{tenant_id}/mine_mobile/",
    tags=["手机验证码认证"],
    auth=None,
    response=UpdateMineMobileOut,
)
def update_mine_mobile(request, tenant_id: str,data:UpdateMineMobileIn):
    """更改手机号码,TODO
    """
    
    return {'error': ErrorCode.OK.value}