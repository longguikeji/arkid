from arkid.core.translation import gettext_default as _
from arkid.core import routers

tag = "mine_logout"
name = _("退出登录")

router = routers.FrontRouter(
    path=tag,
    name=name,
    icon='logout',
    url='/api/v1/tenant/{tenant_id}/mine/logout/'
)