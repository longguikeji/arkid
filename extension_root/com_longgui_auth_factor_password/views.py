from .schema import *
from arkid.core.api import api
from arkid.core.translation import gettext_default as _
from .error import ErrorCode
from arkid.core.error import ErrorDict
from django.contrib.auth.hashers import check_password, make_password
from .models import UserPassword

@api.post(
    "/tenant/{tenant_id}/mine_password/",
    tags=["密码认证因素"],
    response=UpdateMinePasswordOut,
)
def update_mine_password(request, tenant_id: str,data:UpdateMinePasswordIn):
    """更改密码"""
    user = request.user
    user = UserPassword.objects.filter(target=user).first()
    user_password = user.password
    if not user_password or check_password(data.old_password, user_password):
        if data.password == data.confirm_password:
            user.password = make_password(data.password)
            user.save()
            return {'error': ErrorCode.OK.value}
        else:
            return ErrorDict(ErrorCode.TWO_TIME_PASSWORD_MISMATCH)
    
    return ErrorDict(ErrorCode.OLD_PASSWORD_ERROR)