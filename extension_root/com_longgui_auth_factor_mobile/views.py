from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from arkid.core.error import ErrorCode
from .schema import *

@api.post(
    "/tenant/{tenant_id}/mine_mobile/",
    tags=["手机验证码认证因素"],
    response=UpdateMineMobileOut,
)
def update_mine_mobile(request, tenant_id: str,data:UpdateMineMobileIn):
    """更改手机号码,TODO
    """
    
    return {'error': ErrorCode.OK.value}